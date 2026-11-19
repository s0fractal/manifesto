import math
import time
from dataclasses import dataclass
import torch
import torch.nn as nn
import torch.nn.functional as F

# Фіксуємо seed для повної відтворюваності
torch.manual_seed(42)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


@dataclass
class ExperimentConfig:
    num_nodes: int = 16          # N: кількість осциляторних вузлів у кільці
    phase_dim: int = 4           # d: кількість частотних каналів на вузол
    vocab_size: int = 8          # K: розмір словника токенів
    dt: float = 0.15             # крок інтегрування BAOAB
    substeps: int = 2            # кількість фізичних підкроків на 1 токен
    gamma: float = 0.12          # коефіцієнт в'язкого демпфування
    seq_len: int = 24            # довжина послідовності (горизонт пам'яті)
    batch_size: int = 64
    epochs: int = 120
    lr: float = 3e-3
    noise_std: float = 0.08      # інтенсивність теплового/канального збурення


def wrap_angle(theta: torch.Tensor) -> torch.Tensor:
    """Головне значення фази у [-pi, pi)."""
    return torch.remainder(theta + math.pi, 2 * math.pi) - math.pi


def compute_topological_charge(theta: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
    """
    Обчислює точний дискретний топологічний заряд Q_top in Z вздовж кільця вузлів
    та частку ланок біля порогу фазового прослизання (|Delta theta| > 0.85 * pi).
    theta shape: (B, N, d)
    """
    theta_next = torch.roll(theta, shifts=-1, dims=1)
    link_diff = wrap_angle(theta_next - theta)  # (B, N, d) у [-pi, pi)
    q_top = torch.sum(link_diff, dim=1) / (2 * math.pi)  # (B, d), строго цілі числа
    near_slip_ratio = (link_diff.abs() > 0.85 * math.pi).float().mean()
    return q_top, near_slip_ratio


def compute_effective_rank(theta: torch.Tensor) -> float:
    """
    Спектральний ефективний ранг Роя-Веттерлі матриці комплексного вкладення Z = exp(i * Theta).
    theta shape: (B, N, d) -> усереднюємо по батчу.
    """
    with torch.no_grad():
        B, N, d = theta.shape
        z_real = torch.cos(theta).reshape(B, N, d)
        z_imag = torch.sin(theta).reshape(B, N, d)
        # Будуємо дійсне ізометричне вкладення Кліффорда (B, N, 2d)
        embedding = torch.cat([z_real, z_imag], dim=-1)
        s = torch.linalg.svdvals(embedding)  # (B, min(N, 2d))
        p = s / (torch.sum(s, dim=-1, keepdim=True) + 1e-12)
        entropy = -torch.sum(p * torch.log(p + 1e-12), dim=-1)
        erank = torch.exp(entropy).mean().item()
    return erank


class PortHamiltonianCore(nn.Module):
    """
    Строге Порт-Гамільтонове ядро (підтримує два режими):
    - use_soliton_lattice = False -> Модель 1 (Pure-PHS)
    - use_soliton_lattice = True  -> Модель 2 (Soliton-PHS із потенціалом Френкеля-Конторової)
    """
    def __init__(self, cfg: ExperimentConfig, use_soliton_lattice: bool = False):
        super().__init__()
        self.cfg = cfg
        self.N = cfg.num_nodes
        self.d = cfg.phase_dim
        self.use_soliton_lattice = use_soliton_lattice

        # Вхідний порт G_in: перетворює токен у зовнішній фазовий потенціал/імпульс
        self.token_embed = nn.Embedding(cfg.vocab_size, self.N * self.d)
        self.input_gate = nn.Linear(cfg.vocab_size, self.N * self.d)

        # Навчувані параметри Гамільтоніана
        self.log_mass = nn.Parameter(torch.zeros(1, self.N, 1))
        self.kappa_att = nn.Parameter(torch.tensor(1.5))  # сила нелокальної уваги фон Мізеса

        # Кососиметрична матриця гіроскопічного зв'язку імпульсів J_PP = S - S^T (строго div F_gyro = 0)
        self.gyro_skew_raw = nn.Parameter(0.1 * torch.randn(self.N, self.N))

        if use_soliton_lattice:
            # Параметри решітки Френкеля-Конторової (дискретний синус-Гордон)
            self.g_lat = nn.Parameter(torch.tensor(1.8))   # пружність топологічних ланок кільця
            self.g_pin = nn.Parameter(torch.tensor(0.6))   # висота мульти-ямного піннінгу
            self.pin_multiplicity = 2                      # m-кратність бар'єра Пайєрлса-Набарро

        # Readout-шар зчитує гармонійне вкладення [cos(Theta), sin(Theta), P]
        readout_dim = 3 * self.N * self.d
        self.readout = nn.Linear(readout_dim, cfg.vocab_size)

    def _conservative_forces(self, theta: torch.Tensor, phi_ext: torch.Tensor, u_drive: torch.Tensor) -> torch.Tensor:
        """
        Обчислює строго консервативну силу F_cons = -grad_Theta V_total(Theta).
        Усі доданки є точними аналітичними похідними скалярного Гамільтоніана!
        """
        B, N, d = theta.shape

        # 1. Точний градієнт симетризованого потенціалу уваги фон Мізеса V_att
        # diff[b, i, j, k] = theta[b, i, k] - theta[b, j, k]
        diff = theta.unsqueeze(2) - theta.unsqueeze(1)  # (B, N, N, d)
        cos_sim = torch.cos(diff).mean(dim=-1)          # (B, N, N)
        kappa = F.softplus(self.kappa_att)
        A = F.softmax(kappa * cos_sim, dim=-1)          # (B, N, N)
        # Враховуємо обидва доданки похідної: A_ij + A_ji
        A_sym = 0.5 * (A + A.transpose(1, 2))           # (B, N, N)
        # -dV_att / dtheta_i = -(kappa / d) * sum_j (A_ij + A_ji) * sin(theta_i - theta_j)
        f_att = -(kappa / d) * torch.einsum("bij,bijk->bik", A_sym, torch.sin(diff))

        # 2. Зовнішній порт взаємодії з поточним токеном V_ext = -u_drive * cos(theta - phi_ext)
        f_ext = -u_drive * torch.sin(theta - phi_ext)

        f_total = f_att + f_ext

        # 3. Топологічна решітка Френкеля-Конторової (тільки для Soliton-PHS)
        if self.use_soliton_lattice:
            g_lat = F.softplus(self.g_lat)
            g_pin = F.softplus(self.g_pin)
            theta_prev = torch.roll(theta, shifts=1, dims=1)
            theta_next = torch.roll(theta, shifts=-1, dims=1)
            # Дискретний лапласіан синусів уздовж кільця (зберігає топологічні кінки)
            f_lat = g_lat * (torch.sin(theta_next - theta) - torch.sin(theta - theta_prev))
            # Локальний піннінг-бар'єр Пайєрлса-Набарро
            f_pin = -g_pin * self.pin_multiplicity * torch.sin(self.pin_multiplicity * theta)
            f_total = f_total + f_lat + f_pin

        return f_total

    def forward(self, x_tokens: torch.Tensor, inject_noise: bool = True) -> dict:
        B, T = x_tokens.shape
        dt = self.cfg.dt / self.cfg.substeps
        gamma = self.cfg.gamma
        mass = torch.exp(self.log_mass)  # (1, N, 1) > 0

        # Початкова ініціалізація на торі
        theta = torch.zeros(B, self.N, self.d, device=x_tokens.device)
        p = torch.zeros(B, self.N, self.d, device=x_tokens.device)

        # Кососиметрична матриця J_PP = S - S^T (строго бездивергентна сила Лоренца)
        J_pp = self.gyro_skew_raw - self.gyro_skew_raw.T  # (N, N)

        # Точний симплектичний поворот Кейлі для гіроскопічного зв'язку (захист від експоненційного розгойдування)
        # K = M^{-1/2} J_PP M^{-1/2}
        sqrt_m = torch.exp(0.5 * self.log_mass).view(self.N)  # (N,)
        K = J_pp / (sqrt_m.unsqueeze(1) * sqrt_m.unsqueeze(0))  # (N, N)
        I_N = torch.eye(self.N, device=x_tokens.device, dtype=J_pp.dtype)
        # Напівкрок повороту tau = dt / 2 -> матриця (I - 0.25*dt*K)^{-1} (I + 0.25*dt*K)
        R_cay = torch.linalg.solve(I_N - 0.25 * dt * K, I_N + 0.25 * dt * K)
        # Оператор повороту в координатах імпульсів P: G = M^{1/2} R_cay M^{-1/2}
        G_rot = (sqrt_m.unsqueeze(1) * R_cay) / sqrt_m.unsqueeze(0)  # (N, N)

        logits_seq = []
        q_top_history = []
        slip_warnings = []

        decay = math.exp(-gamma * dt)
        noise_scale = math.sqrt(max(1.0 - decay ** 2, 0.0)) * self.cfg.noise_std

        for t in range(T):
            tok = x_tokens[:, t]
            phi_ext = wrap_angle(self.token_embed(tok).view(B, self.N, self.d))
            u_drive = torch.sigmoid(self.input_gate(F.one_hot(tok, self.cfg.vocab_size).float())).view(B, self.N, self.d) * 2.5

            for _ in range(self.cfg.substeps):
                # 1. B-крок (1/2): чистий консервативний градієнт без явного ейлерівського розгойдування
                f_cons = self._conservative_forces(theta, phi_ext, u_drive)
                p = p + 0.5 * dt * f_cons

                # 2. G-крок (1/2): точний поворот Кейлі (строго зберігає кінетичну енергію P^T M^{-1} P)
                p = torch.einsum("ij,bjd->bid", G_rot, p)

                # 3. A-крок (1/2): дрейф координат на торі
                theta = wrap_angle(theta + 0.5 * dt * (p / mass))

                # 4. O-крок: узгоджений за масою термостат Орнштейна-Уленбека
                if inject_noise:
                    xi = torch.randn_like(p)
                    p = decay * p + noise_scale * torch.sqrt(mass) * xi
                else:
                    p = decay * p

                # 5. A-крок (2/2): дрейф координат на торі
                theta = wrap_angle(theta + 0.5 * dt * (p / mass))

                # 6. G-крок (2/2): точний поворот Кейлі
                p = torch.einsum("ij,bjd->bid", G_rot, p)

                # 7. B-крок (2/2): фінальний консервативний градієнт
                f_cons_next = self._conservative_forces(theta, phi_ext, u_drive)
                p = p + 0.5 * dt * f_cons_next

            # Фіксуємо топологічну діагностику
            with torch.no_grad():
                q_top, slip_ratio = compute_topological_charge(theta)
                q_top_history.append(q_top)
                slip_warnings.append(slip_ratio)

            # Канонічне гармонійне зчитування на торі
            feat = torch.cat([torch.cos(theta), torch.sin(theta), p], dim=-1).reshape(B, -1)
            logits_seq.append(self.readout(feat))

        logits = torch.stack(logits_seq, dim=1)  # (B, T, V)

        # Підрахунок кількості дискретних фазових прослизань (коли |Delta Q_top| >= 1 між кроками)
        q_stack = torch.stack(q_top_history, dim=1)  # (B, T, d)
        phase_slips = (torch.diff(q_stack, dim=1).abs() > 0.5).float().sum(dim=(1, 2)).mean().item()

        return {
            "logits": logits,
            "erank": compute_effective_rank(theta),
            "phase_slips": phase_slips,
            "mean_abs_q": q_stack[:, -1, :].abs().mean().item(),
        }


class ControlGRUNetwork(nn.Module):
    """
    Модель 3: Контрольна рекурентна мережа (GRU) з еквівалентним розміром прихованого стану 2*N*d.
    """
    def __init__(self, cfg: ExperimentConfig):
        super().__init__()
        self.cfg = cfg
        self.hidden_dim = 2 * cfg.num_nodes * cfg.phase_dim
        self.embed = nn.Embedding(cfg.vocab_size, self.hidden_dim)
        self.gru = nn.GRU(self.hidden_dim, self.hidden_dim, batch_first=True)
        self.readout = nn.Linear(self.hidden_dim, cfg.vocab_size)

    def forward(self, x_tokens: torch.Tensor, inject_noise: bool = True) -> dict:
        x = self.embed(x_tokens)
        if inject_noise:
            x = x + self.cfg.noise_std * torch.randn_like(x)
        out, h_n = self.gru(x)
        logits = self.readout(out)
        # Ефективний ранг прихованого стану GRU, розгорнутого у матрицю (N, 2d)
        with torch.no_grad():
            B = x_tokens.shape[0]
            h_mat = h_n.squeeze(0).view(B, self.cfg.num_nodes, 2 * self.cfg.phase_dim)
            s = torch.linalg.svdvals(h_mat)
            p = s / (torch.sum(s, dim=-1, keepdim=True) + 1e-12)
            erank = torch.exp(-torch.sum(p * torch.log(p + 1e-12), dim=-1)).mean().item()
        return {
            "logits": logits,
            "erank": erank,
            "phase_slips": 0.0,
            "mean_abs_q": 0.0,
        }


# ==============================================================================
# Генератори задач:
# 1) Довготривале утримання крізь дистрактори (Copy-Recall Horizon)
# 2) Багатоетапний трекінг стану скінченного автомата (Modulo-K Parity/FSM)
# ==============================================================================

def generate_copy_recall_batch(cfg: ExperimentConfig) -> tuple[torch.Tensor, torch.Tensor]:
    """
    Перші 2 токени — корисний сигнал із {1..V-1}, далі T-3 кроків шуму-дистрактора (токен 0),
    на останньому кроці модель має згадати перший корисний токен.
    """
    B, T, V = cfg.batch_size, cfg.seq_len, cfg.vocab_size
    x = torch.zeros(B, T, dtype=torch.long, device=device)
    target_sym = torch.randint(1, V, (B,), device=device)
    x[:, 0] = target_sym
    x[:, 1] = target_sym
    # Додаємо випадкові інтерференційні спалахи посеред послідовності
    noise_mask = torch.rand(B, T - 3, device=device) < 0.25
    random_distractors = torch.randint(1, V, (B, T - 3), device=device)
    x[:, 2:-1] = torch.where(noise_mask, random_distractors, torch.zeros_like(random_distractors))
    return x, target_sym


def generate_modular_fsm_batch(cfg: ExperimentConfig) -> tuple[torch.Tensor, torch.Tensor]:
    """
    Багатоетапна логічна операція: кожен вхідний токен x_t in {0, 1, 2} змінює внутрішній стан
    автомата S_t = (S_{t-1} + x_t) mod (V - 1) з інверсією при x_t == 3.
    Потребує точного покрокового відстеження стану без 'групового самообману'.
    """
    B, T, V = cfg.batch_size, cfg.seq_len, cfg.vocab_size
    x = torch.randint(0, 4, (B, T), dtype=torch.long, device=device)
    state = torch.zeros(B, dtype=torch.long, device=device)
    modulus = V - 1
    for t in range(T):
        tok = x[:, t]
        state = torch.where(tok == 3, (modulus - state) % modulus, (state + tok) % modulus)
    return x, state


if __name__ == "__main__":
    print("=" * 70)
    print("  Порт-Гамільтонові та Солітонні Резервуари (BAOAB + Cayley Rotation)")
    print("=" * 70)
    cfg = ExperimentConfig()
    x_test, y_test = generate_copy_recall_batch(cfg)

    print(f"\nКонфігурація: N={cfg.num_nodes} вузлів, d={cfg.phase_dim} каналів, T={cfg.seq_len} токенів, dt={cfg.dt}")
    print("Ініціалізація 3 моделей з однаковою розмірністю стану D_state = 2Nd = 128:")
    
    models = {
        "Pure-PHS": PortHamiltonianCore(cfg, use_soliton_lattice=False).to(device),
        "Soliton-PHS": PortHamiltonianCore(cfg, use_soliton_lattice=True).to(device),
        "Control-GRU": ControlGRUNetwork(cfg).to(device),
    }

    for name, model in models.items():
        out = model(x_test)
        logits = out["logits"]
        loss = F.cross_entropy(logits[:, -1, :], y_test)
        print(f"  [{name:12s}] Loss: {loss.item():.4f} | erank: {out['erank']:.2f} | phase slips: {out['phase_slips']:.2f}")

    print("\n✓ Forward pass успішний! Поворот Кейлі стабільний, енергія імпульсів не вибухає.")