/-
Terminology-through-Lean — PoC (Book-I-style scope note).

WHAT THIS SHOWS: a glossary term's committed structure can live as Lean
definitions, so that
  • a LEGAL relation between terms is a machine-CHECKED theorem;
  • an ILLEGAL cast (FLOW-GLOSSARY's illegal-cast discipline) is not merely
    "unproven" but machine-REFUTED by an exhibited countermodel.
The Lean kernel re-checks this independently of any LLM lineage — the one
out-of-lineage validator the project otherwise lacks (threat-model C3).

WHAT THIS DOES NOT SHOW: that any implementation (Python/TS) conforms to these
definitions (separate obligation), nor that untypeable terms (Value, Dignity)
belong here at all — they do not; only `Defined`-status terms are Lean-able.
-/
namespace FlowGlossary

/-- The stipulated modal structure over an arbitrary state space `σ`.
    Reachable ⊇ Viable ⊇ Flourishing are the committed inclusions. -/
structure Modal (σ : Type) where
  Reachable    : σ → Prop
  Viable       : σ → Prop          -- can be sustained
  Flourishing  : σ → Prop
  flour_viable : ∀ s, Flourishing s → Viable s      -- stipulation
  viable_reach : ∀ s, Viable s → Reachable s        -- stipulation

/-- LEGAL cast Flourishing ⇒ Reachable is DERIVABLE — a checked theorem. -/
theorem flourishing_reachable {σ} (M : Modal σ) :
    ∀ s, M.Flourishing s → M.Reachable s :=
  fun s h => M.viable_reach s (M.flour_viable s h)

/-- A countermodel: everything is Reachable, but only `true` is Viable. -/
def Counter : Modal Bool where
  Reachable    := fun _ => True
  Viable       := fun s => s = true
  Flourishing  := fun s => s = true
  flour_viable := fun _ h => h
  viable_reach := fun _ _ => trivial

/-- The ILLEGAL cast Reachable ⇒ Viable (CanDo ⇏ CanSustain) is machine-REFUTED:
    in `Counter`, `false` is Reachable but not Viable. -/
theorem illegal_cast_reachable_viable_refuted :
    ¬ (∀ s, Counter.Reachable s → Counter.Viable s) := by
  intro h
  have hv : Counter.Viable false := h false trivial
  simp [Counter] at hv

end FlowGlossary
