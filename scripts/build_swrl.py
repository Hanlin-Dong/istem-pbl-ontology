#!/usr/bin/env python3
"""
build_swrl.py — Real SWRL Rules for IE-PBL Ontology (v2.0).

Implements SWRL rules using owlready2's Imp API with Pellet reasoner.
This replaces the previous SPARQL-based simulation (now deleted).

Two rule sets:
  (A) Orchestration: DiscourseAction → VirtualAgent triggers
  (B) Assessment: PBL events → PerformanceTrace → CompetencyDimension

Rules are applied via Pellet's SWRL-enabled reasoning.

Reference: W3C SWRL Submission (https://www.w3.org/Submission/SWRL/)
"""

import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from owlready2 import *
from config import IRI, RULES_DIR
from tbox import build_all_tbox, validate_with_pellet
from build_vignette import build_vignette


def _collect_all_ontologies():
    """Gather all module ontologies for SWRL namespace resolution."""
    ontos = []
    seen = set()
    for c in default_world.classes():
        o = c.namespace.ontology
        if o.base_iri not in seen:
            seen.add(o.base_iri)
            ontos.append(o)
    return ontos


def build_swrl_rules(C):
    """
    Create SWRL rules using owlready2's Imp API with real reasoning.

    Each rule is registered in the appropriate ontology namespace so that
    Pellet's SWRL engine can process it during sync_reasoner_pellet().

    Returns dict of rule_name → Imp object.
    """
    rules = {}
    ontos = _collect_all_ontologies()

    # Use the first available ontology as the Imp namespace
    ns_onto = ontos[0] if ontos else None
    if ns_onto is None:
        print("ERROR: No ontology found for SWRL namespace")
        return rules

    # ═════════════════════════════════════════════════════════════
    # (A) ORCHESTRATION RULES — DiscourseAction → VirtualAgent
    # ═════════════════════════════════════════════════════════════

    # R1: FailureReporting in Implementation phase → MetacognitiveChallenger
    # Rationale: Productive Failure theory (Kapur, 2008)
    # Subsumption: matches EiE_Create ⊑ Implementation, CDIO_Implement ⊑ Implementation
    r1 = Imp(namespace=ns_onto)
    r1.set_as_rule(
        "FailureReporting(?da), occursInPhase(?da, ?phase), "
        "Implementation(?phase), MetacognitiveChallenger(?agent), "
        "monitorsTeam(?agent, ?team), isAttributedTo(?da, ?learner), "
        "Learner(?learner), isMemberOf(?learner, ?team) "
        "-> triggersAgent(?da, ?agent)",
        namespaces=ontos
    )
    r1.label.append("R1: FailureReporting+Implementation→MetacognitiveChallenger@en")
    rules["R1_FailureImpl_Meta"] = r1

    # R2: HelpSeeking in SolutionIdeation phase → ProceduralGuide
    # Subsumption: matches EiE_Plan ⊑ SolutionIdeation, CDIO_Design ⊑ SolutionIdeation
    r2 = Imp(namespace=ns_onto)
    r2.set_as_rule(
        "HelpSeeking(?da), occursInPhase(?da, ?phase), "
        "SolutionIdeation(?phase), ProceduralGuide(?agent), "
        "monitorsTeam(?agent, ?team), isAttributedTo(?da, ?learner), "
        "Learner(?learner), isMemberOf(?learner, ?team) "
        "-> triggersAgent(?da, ?agent)",
        namespaces=ontos
    )
    r2.label.append("R2: HelpSeeking+SolutionIdeation→ProceduralGuide@en")
    rules["R2_HelpIdeation_Procedural"] = r2

    # R3: PeerArgumentation + referencesConcept → ConceptualExpert
    # Rationale: CSCL epistemic discourse + domain knowledge scaffolding
    r3 = Imp(namespace=ns_onto)
    r3.set_as_rule(
        "PeerArgumentation(?da), referencesConcept(?da, ?concept), "
        "Concept(?concept), ConceptualExpert(?agent), "
        "monitorsTeam(?agent, ?team), isAttributedTo(?da, ?learner), "
        "Learner(?learner), isMemberOf(?learner, ?team) "
        "-> triggersAgent(?da, ?agent)",
        namespaces=ontos
    )
    r3.label.append("R3: PeerArgumentation+Concept→ConceptualExpert@en")
    rules["R3_PeerArg_Conceptual"] = r3

    # R4: IdeaGeneration in SolutionIdeation phase → DivergentBrainstormer
    # Subsumption: matches EiE_Imagine ⊑ SolutionIdeation
    r4 = Imp(namespace=ns_onto)
    r4.set_as_rule(
        "IdeaGeneration(?da), occursInPhase(?da, ?phase), "
        "SolutionIdeation(?phase), DivergentBrainstormer(?agent), "
        "monitorsTeam(?agent, ?team), isAttributedTo(?da, ?learner), "
        "Learner(?learner), isMemberOf(?learner, ?team) "
        "-> triggersAgent(?da, ?agent)",
        namespaces=ontos
    )
    r4.label.append("R4: IdeaGeneration+Imagine→DivergentBrainstormer@en")
    rules["R4_IdeaImagine_Divergent"] = r4

    # R5: ProcessConfusion → ProceduralGuide (any phase)
    # Rationale: Hannafin Procedural — when student loses track of process
    r5 = Imp(namespace=ns_onto)
    r5.set_as_rule(
        "ProcessConfusion(?da), ProceduralGuide(?agent), "
        "monitorsTeam(?agent, ?team), isAttributedTo(?da, ?learner), "
        "Learner(?learner), isMemberOf(?learner, ?team) "
        "-> triggersAgent(?da, ?agent)",
        namespaces=ontos
    )
    r5.label.append("R5: ProcessConfusion→ProceduralGuide@en")
    rules["R5_Confusion_Procedural"] = r5

    # R6: EmotiveExpression → AffectiveSupporter (revised after Experiment B)
    # Rationale: emotion calls for affective support, not cognitive challenge.
    r6 = Imp(namespace=ns_onto)
    r6.set_as_rule(
        "EmotiveExpression(?da), AffectiveSupporter(?agent), "
        "monitorsTeam(?agent, ?team), isAttributedTo(?da, ?learner), "
        "Learner(?learner), isMemberOf(?learner, ?team) "
        "-> triggersAgent(?da, ?agent)",
        namespaces=ontos
    )
    r6.label.append("R6: EmotiveExpression→AffectiveSupporter@en")
    rules["R6_Emotive_Affective"] = r6

    # R7: SerendipitousDiscovery → DivergentBrainstormer
    # Rationale: Teacher review — unexpected discoveries feed creative ideation
    r7 = Imp(namespace=ns_onto)
    r7.set_as_rule(
        "SerendipitousDiscovery(?da), DivergentBrainstormer(?agent), "
        "monitorsTeam(?agent, ?team), isAttributedTo(?da, ?learner), "
        "Learner(?learner), isMemberOf(?learner, ?team) "
        "-> triggersAgent(?da, ?agent)",
        namespaces=ontos
    )
    r7.label.append("R7: SerendipitousDiscovery→DivergentBrainstormer@en")
    rules["R7_Serendipity_Divergent"] = r7

    # R8: HypothesisProposing in ScientificInvestigation phase → ConceptualExpert
    # Rationale: hypothesis formulation needs domain knowledge scaffolding
    r8 = Imp(namespace=ns_onto)
    r8.set_as_rule(
        "HypothesisProposing(?da), occursInPhase(?da, ?phase), "
        "ScientificInvestigation(?phase), ConceptualExpert(?agent), "
        "monitorsTeam(?agent, ?team), isAttributedTo(?da, ?learner), "
        "Learner(?learner), isMemberOf(?learner, ?team) "
        "-> triggersAgent(?da, ?agent)",
        namespaces=ontos
    )
    r8.label.append("R8: HypothesisProposing+ScientificInvestigation→ConceptualExpert@en")
    rules["R8_HypothesisSci_Conceptual"] = r8

    # R9: EvidenceAnalyzing → ConceptualExpert
    # Rationale: data interpretation benefits from domain expertise
    r9 = Imp(namespace=ns_onto)
    r9.set_as_rule(
        "EvidenceAnalyzing(?da), ConceptualExpert(?agent), "
        "monitorsTeam(?agent, ?team), isAttributedTo(?da, ?learner), "
        "Learner(?learner), isMemberOf(?learner, ?team) "
        "-> triggersAgent(?da, ?agent)",
        namespaces=ontos
    )
    r9.label.append("R9: EvidenceAnalyzing→ConceptualExpert@en")
    rules["R9_Evidence_Conceptual"] = r9

    # R10: PrincipleFormulating → MetacognitiveChallenger
    # Rationale: synthesizing principles requires metacognitive reflection
    r10 = Imp(namespace=ns_onto)
    r10.set_as_rule(
        "PrincipleFormulating(?da), MetacognitiveChallenger(?agent), "
        "monitorsTeam(?agent, ?team), isAttributedTo(?da, ?learner), "
        "Learner(?learner), isMemberOf(?learner, ?team) "
        "-> triggersAgent(?da, ?agent)",
        namespaces=ontos
    )
    r10.label.append("R10: PrincipleFormulating→MetacognitiveChallenger@en")
    rules["R10_Principle_Meta"] = r10

    # R11: SafetyIntervention + overridesAgent → SafetyMonitor
    # Rationale: When instructor overrides an agent for safety reasons,
    # the SafetyMonitor should be alerted to track the intervention.
    r11 = Imp(namespace=ns_onto)
    r11.set_as_rule(
        "SafetyIntervention(?intv), overridesAgent(?intv, ?agent) "
        "-> triggersAgent(?intv, SafetyMonitor)",
        namespaces=ontos
    )
    r11.label.append("R11: SafetyIntervention+overridesAgent→SafetyMonitor@en")
    rules["R11_Safety_SafetyMon"] = r11
    # R12: DesignJustification in Implementation phase → ConceptualExpert
    # Rationale (revised after Experiment B): a design justification is a "why"
    # (conceptual basis), not a "how" (procedural step).
    r12 = Imp(namespace=ns_onto)
    r12.set_as_rule(
        "DesignJustification(?da), occursInPhase(?da, ?phase), "
        "Implementation(?phase), ConceptualExpert(?agent), "
        "monitorsTeam(?agent, ?team), isAttributedTo(?da, ?learner), "
        "Learner(?learner), isMemberOf(?learner, ?team) "
        "-> triggersAgent(?da, ?agent)",
        namespaces=ontos
    )
    r12.label.append("R12: DesignJustification+Implementation→ConceptualExpert@en")
    rules["R12_DesignJust_Conceptual"] = r12

    # R13: SocialBonding → AffectiveSupporter (retargeted after B2-R: raters'
    # written comments converged on routing social bonding to affective support)
    r13 = Imp(namespace=ns_onto)
    r13.set_as_rule(
        "SocialBonding(?da), AffectiveSupporter(?agent), "
        "monitorsTeam(?agent, ?team), isAttributedTo(?da, ?learner), "
        "Learner(?learner), isMemberOf(?learner, ?team) "
        "-> triggersAgent(?da, ?agent)",
        namespaces=ontos
    )
    r13.label.append("R13: SocialBonding→AffectiveSupporter@en")
    rules["R13_Social_Affective"] = r13

    # R14: PeerTutoring → ConceptualExpert
    # Rationale: Peer tutoring indicates knowledge construction — expert can reinforce
    r14 = Imp(namespace=ns_onto)
    r14.set_as_rule(
        "PeerTutoring(?da), ConceptualExpert(?agent), "
        "monitorsTeam(?agent, ?team), isAttributedTo(?da, ?learner), "
        "Learner(?learner), isMemberOf(?learner, ?team) "
        "-> triggersAgent(?da, ?agent)",
        namespaces=ontos
    )
    r14.label.append("R14: PeerTutoring→ConceptualExpert@en")
    rules["R14_PeerTutor_Conceptual"] = r14

    # R15: Agreement/Disagreement → MetacognitiveChallenger
    # Rationale: Simple agreement/disagreement can be scaffolded into deeper epistemic discourse
    r15 = Imp(namespace=ns_onto)
    r15.set_as_rule(
        "Agreement(?da), MetacognitiveChallenger(?agent), "
        "monitorsTeam(?agent, ?team), isAttributedTo(?da, ?learner), "
        "Learner(?learner), isMemberOf(?learner, ?team) "
        "-> triggersAgent(?da, ?agent)",
        namespaces=ontos
    )
    r15.label.append("R15: Agreement→MetacognitiveChallenger@en")
    rules["R15_Agreement_Meta"] = r15

    r15b = Imp(namespace=ns_onto)
    r15b.set_as_rule(
        "Disagreement(?da), ProceduralGuide(?agent), "
        "monitorsTeam(?agent, ?team), isAttributedTo(?da, ?learner), "
        "Learner(?learner), isMemberOf(?learner, ?team) "
        "-> triggersAgent(?da, ?agent)",
        namespaces=ontos
    )
    r15b.label.append("R15b: Disagreement→ProceduralGuide@en")
    rules["R15b_Disagreement_Procedural"] = r15b

    # R16: Gesturing → DivergentBrainstormer
    # Rationale: Non-verbal spatial expression can feed creative ideation
    r16 = Imp(namespace=ns_onto)
    r16.set_as_rule(
        "Gesturing(?da), DivergentBrainstormer(?agent), "
        "monitorsTeam(?agent, ?team), isAttributedTo(?da, ?learner), "
        "Learner(?learner), isMemberOf(?learner, ?team) "
        "-> triggersAgent(?da, ?agent)",
        namespaces=ontos
    )
    r16.label.append("R16: Gesturing→DivergentBrainstormer@en")
    rules["R16_Gesture_Divergent"] = r16

    # R17: PhysicalPrototyping + hasModality "physical" → SafetyMonitor
    # Rationale: When students engage in hands-on physical prototyping,
    # the SafetyMonitor should be alerted for proactive risk monitoring.
    r17 = Imp(namespace=ns_onto)
    r17.set_as_rule(
        "PhysicalPrototyping(?da), hasModality(?da, \"physical\"), "
        "SafetyMonitor(?agent), "
        "monitorsTeam(?agent, ?team), isAttributedTo(?da, ?learner), "
        "Learner(?learner), isMemberOf(?learner, ?team) "
        "-> triggersAgent(?da, ?agent)",
        namespaces=ontos
    )
    r17.label.append("R17: PhysicalPrototyping→SafetyMonitor@en")
    rules["R17_Physical_Safety"] = r17

    # R18: HelpSeeking + Implementation phase → ProceduralGuide
    # Rationale: During Implementation (Create/Build phase), procedural
    # help-seeking needs immediate guidance.
    # NOTE: R2 already covers HelpSeeking + SolutionIdeation.
    #       This is a DIFFERENT rule for Implementation phase.
    r18 = Imp(namespace=ns_onto)
    r18.set_as_rule(
        "HelpSeeking(?da), occursInPhase(?da, ?phase), "
        "Implementation(?phase), ProceduralGuide(?agent), "
        "monitorsTeam(?agent, ?team), isAttributedTo(?da, ?learner), "
        "Learner(?learner), isMemberOf(?learner, ?team) "
        "-> triggersAgent(?da, ?agent)",
        namespaces=ontos
    )
    r18.label.append("R18: HelpSeeking+Implementation→ProceduralGuide@en")
    rules["R18_HelpImpl_Procedural"] = r18

    # R19: KnowledgeSharing + referencesConcept + ScientificInvestigation phase → ConceptualExpert
    # Rationale: When a student shares knowledge about a concept during scientific
    # investigation, the expert should validate and extend.
    r19 = Imp(namespace=ns_onto)
    r19.set_as_rule(
        "KnowledgeSharing(?da), referencesConcept(?da, ?concept), "
        "Concept(?concept), occursInPhase(?da, ?phase), "
        "ScientificInvestigation(?phase), ConceptualExpert(?agent), "
        "monitorsTeam(?agent, ?team), isAttributedTo(?da, ?learner), "
        "Learner(?learner), isMemberOf(?learner, ?team) "
        "-> triggersAgent(?da, ?agent)",
        namespaces=ontos
    )
    r19.label.append("R19: KnowledgeSharing+Concept+ScientificInvestigation→ConceptualExpert@en")
    rules["R19_KnowledgeSci_Conceptual"] = r19

    # R20: Demonstration → MetacognitiveChallenger
    # Rationale: When a student demonstrates a result, the metacognitive coach
    # should prompt reflection ("How did you achieve this? What would you change?").
    r20 = Imp(namespace=ns_onto)
    r20.set_as_rule(
        "Demonstration(?da), MetacognitiveChallenger(?agent), "
        "monitorsTeam(?agent, ?team), isAttributedTo(?da, ?learner), "
        "Learner(?learner), isMemberOf(?learner, ?team) "
        "-> triggersAgent(?da, ?agent)",
        namespaces=ontos
    )
    r20.label.append("R20: Demonstration→MetacognitiveChallenger@en")
    rules["R20_Demo_Meta"] = r20

    # R21: PeerEncouragement → AffectiveSupporter (revised after Experiment B)
    # Rationale: encouragement is affective support, not divergent ideation.
    r21 = Imp(namespace=ns_onto)
    r21.set_as_rule(
        "PeerEncouragement(?da), AffectiveSupporter(?agent), "
        "monitorsTeam(?agent, ?team), isAttributedTo(?da, ?learner), "
        "Learner(?learner), isMemberOf(?learner, ?team) "
        "-> triggersAgent(?da, ?agent)",
        namespaces=ontos
    )
    r21.label.append("R21: PeerEncouragement→AffectiveSupporter@en")
    rules["R21_PeerEncourage_Affective"] = r21

    # R22: ConstraintReasoningAction → ProceduralGuide
    r22 = Imp(namespace=ns_onto)
    r22.set_as_rule(
        "ConstraintReasoningAction(?da), ProceduralGuide(?agent), "
        "monitorsTeam(?agent, ?team), isAttributedTo(?da, ?learner), "
        "Learner(?learner), isMemberOf(?learner, ?team) "
        "-> triggersAgent(?da, ?agent)",
        namespaces=ontos
    )
    r22.label.append("R22: ConstraintReasoningAction→ProceduralGuide@en")
    rules["R22_Constraint_Procedural"] = r22

    # R23: Cross-team discourse → MetacognitiveChallenger
    r23 = Imp(namespace=ns_onto)
    r23.set_as_rule(
        "directedToTeam(?da, ?team), MetacognitiveChallenger(?agent), "
        "monitorsTeam(?agent, ?team), isAttributedTo(?da, ?learner), "
        "Learner(?learner), isMemberOf(?learner, ?team) "
        "-> triggersAgent(?da, ?agent)",
        namespaces=ontos
    )
    r23.label.append("R23: CrossTeamDiscourse→MetacognitiveChallenger@en")
    rules["R23_CrossTeam_Meta"] = r23


    # ═════════════════════════════════════════════════════════════
    # (B) ASSESSMENT RULES — Event → PerformanceTrace → Competency
    # ═════════════════════════════════════════════════════════════

    # A1: FailureReporting → traces EngineeringThinking
    # Rationale: ECD evidence model (Mislevy et al., 2003)
    a1 = Imp(namespace=ns_onto)
    a1.set_as_rule(
        "FailureReporting(?da), derivedFromEvent(?trace, ?da), "
        "PerformanceTrace(?trace) "
        "-> tracesCompetency(?trace, EngineeringThinking)",
        namespaces=ontos
    )
    a1.label.append("A1: FailureReporting→EngineeringThinking@en")
    rules["A1_Failure_ET"] = a1

    # A2: IntegrationBridge generated in activity → InterdisciplinaryIntegration
    a2 = Imp(namespace=ns_onto)
    a2.set_as_rule(
        "IntegrationBridge(?bridge), generatedInActivity(?bridge, ?act), "
        "generatesTrace(?act, ?trace), PerformanceTrace(?trace) "
        "-> tracesCompetency(?trace, InterdisciplinaryIntegration)",
        namespaces=ontos
    )
    a2.label.append("A2: IntegrationBridge→InterdisciplinaryIntegration@en")
    rules["A2_Bridge_II"] = a2

    # A3: PeerArgumentation + interaction → CollaborativeTeamwork
    a3 = Imp(namespace=ns_onto)
    a3.set_as_rule(
        "PeerArgumentation(?da), isAttributedTo(?da, ?learner1), "
        "interactsWith(?learner1, ?learner2), "
        "derivedFromEvent(?trace, ?da), PerformanceTrace(?trace) "
        "-> tracesCompetency(?trace, CollaborativeTeamwork)",
        namespaces=ontos
    )
    a3.label.append("A3: PeerArg+Interaction→CollaborativeTeamwork@en")
    rules["A3_PeerArg_Collab"] = a3

    # A4: KnowledgeSharing → EngineeringThinking
    a4 = Imp(namespace=ns_onto)
    a4.set_as_rule(
        "KnowledgeSharing(?da), derivedFromEvent(?trace, ?da), "
        "PerformanceTrace(?trace) "
        "-> tracesCompetency(?trace, EngineeringThinking)",
        namespaces=ontos
    )
    a4.label.append("A4: KnowledgeSharing→EngineeringThinking@en")
    rules["A4_Knowledge_ET"] = a4

    # A6: IdeaGeneration → CreativityAndInnovation
    a6 = Imp(namespace=ns_onto)
    a6.set_as_rule(
        "IdeaGeneration(?da), derivedFromEvent(?trace, ?da), "
        "PerformanceTrace(?trace) "
        "-> tracesCompetency(?trace, CreativityAndInnovation)",
        namespaces=ontos
    )
    a6.label.append("A6: IdeaGeneration→CreativityAndInnovation@en")
    rules["A6_IdeaGen_CI"] = a6

    # A6b: SerendipitousDiscovery → CreativityAndInnovation
    a6b = Imp(namespace=ns_onto)
    a6b.set_as_rule(
        "SerendipitousDiscovery(?da), derivedFromEvent(?trace, ?da), "
        "PerformanceTrace(?trace) "
        "-> tracesCompetency(?trace, CreativityAndInnovation)",
        namespaces=ontos
    )
    a6b.label.append("A6b: SerendipitousDiscovery→CreativityAndInnovation@en")
    rules["A6b_Serendipity_CI"] = a6b

    # A7: Reflection with critical-reflection depth → MetacognitiveSelfRegulation
    # v4.0: re-grounded on the hasReflectionLevel chain — CriticalReflection is a
    # ReflectionLevel (Kember), so the event must carry the level, not be one.
    a7 = Imp(namespace=ns_onto)
    a7.set_as_rule(
        "Reflection(?da), hasReflectionLevel(?da, ?lvl), CriticalReflection(?lvl), "
        "derivedFromEvent(?trace, ?da), "
        "PerformanceTrace(?trace) "
        "-> tracesCompetency(?trace, MetacognitiveSelfRegulation)",
        namespaces=ontos
    )
    a7.label.append("A7: CriticalReflection→MetacognitiveSelfRegulation@en")
    rules["A7_CriticalReflection_MSR"] = a7

    # A8: ConstraintReasoningAction → EngineeringThinking
    a8 = Imp(namespace=ns_onto)
    a8.set_as_rule(
        "ConstraintReasoningAction(?da), derivedFromEvent(?trace, ?da), "
        "PerformanceTrace(?trace) "
        "-> tracesCompetency(?trace, EngineeringThinking)",
        namespaces=ontos
    )
    a8.label.append("A8: ConstraintReasoning→EngineeringThinking@en")
    rules["A8_Constraint_ET"] = a8

    # A9: ValuePerspective expressed → InterdisciplinaryIntegration
    a9 = Imp(namespace=ns_onto)
    a9.set_as_rule(
        "expressesPerspective(?da, ?vp), ValuePerspective(?vp), "
        "derivedFromEvent(?trace, ?da), PerformanceTrace(?trace) "
        "-> tracesCompetency(?trace, InterdisciplinaryIntegration)",
        namespaces=ontos
    )
    a9.label.append("A9: ValuePerspective→InterdisciplinaryIntegration@en")
    rules["A9_ValuePerspective_II"] = a9

    print(f"  ✓ {len(rules)} SWRL rules created via Imp API")
    return rules


def verify_swrl_inferences(C, rules):
    """
    Run Pellet reasoner with SWRL rules and report inferred assertions.

    After sync_reasoner_pellet() with SWRL rules, check for:
      - inferred triggersAgent relationships
      - inferred tracesCompetency relationships
    """
    print("\nRunning Pellet reasoner with SWRL rules (real inference)...")
    try:
        sync_reasoner_pellet(infer_property_values=True, debug=0)
        print("✓ Pellet SWRL reasoning complete")
    except Exception as e:
        print(f"✗ Reasoner error: {e}")
        return {"orchestration": [], "assessment": []}

    results = {"orchestration": [], "assessment": []}

    for ind in default_world.individuals():
        # Check inferred triggersAgent
        if hasattr(ind, "triggersAgent"):
            for agent in ind.triggersAgent:
                da_type = ""
                for t in ind.is_a:
                    if hasattr(t, "name") and t.name not in ("DiscourseAction", "Thing", "NamedIndividual"):
                        da_type = t.name
                        break
                text = ""
                if hasattr(ind, "utteranceText") and ind.utteranceText:
                    text = ind.utteranceText[0][:60]
                results["orchestration"].append({
                    "da": ind.name, "type": da_type,
                    "agent": agent.name, "text": text,
                })

        # Check inferred tracesCompetency
        if hasattr(ind, "tracesCompetency"):
            for comp in ind.tracesCompetency:
                score = ind.competencyScore[0] if hasattr(ind, "competencyScore") and ind.competencyScore else "?"
                results["assessment"].append({
                    "trace": ind.name, "competency": comp.name, "score": score,
                })

    return results


def main():
    print("=" * 60)
    print("SWRL Rules: Real Inference via Pellet + owlready2 Imp API")
    print("=" * 60)

    # 1. Build TBox + ABox
    C = build_all_tbox()
    abox = build_vignette(C)
    n_ind = len(list(default_world.individuals()))
    print(f"\n  TBox + ABox: {n_ind} individuals")

    # 2. Create SWRL rules
    print("\nCreating SWRL rules via owlready2 Imp API...")
    rules = build_swrl_rules(C)

    # 3. Run Pellet with SWRL reasoning
    results = verify_swrl_inferences(C, rules)

    # 4. Report
    print("\n" + "=" * 60)
    print("SWRL INFERENCE RESULTS")
    print("=" * 60)

    print(f"\nOrchestration — triggersAgent inferred ({len(results['orchestration'])}):")
    for r in results["orchestration"]:
        print(f"  ⚡ {r['type']}({r['da']}) → {r['agent']}")

    print(f"\nAssessment — tracesCompetency inferred ({len(results['assessment'])}):")
    for r in results["assessment"]:
        print(f"  📊 {r['trace']} → {r['competency']} (score: {r['score']})")

    # 5. Verify overall consistency
    validate_with_pellet()

    print("\n✅ SWRL inference complete")
    return results


if __name__ == "__main__":
    main()
