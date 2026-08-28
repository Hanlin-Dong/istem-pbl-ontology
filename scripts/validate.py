#!/usr/bin/env python3
"""
validate.py — Unified validation entry point for the IE-PBL Ontology.

Usage:
    python scripts/validate.py              # Full validation (TBox + properties)
    python scripts/validate.py --json       # JSON output for CI consumption
"""

import sys
import os
import json

sys.path.insert(0, os.path.dirname(__file__))

from tbox import build_all_tbox, validate_with_pellet
from owlready2 import default_world, ThingClass
from owl_helpers import declare_covering


def check_covering_axioms(C):
    """Verify all covering axioms have correct subclass membership."""
    report = []

    covering_pairs = [
        # M1: Core
        ("Phase", ["ProblemScoping", "SolutionIdeation", "ScientificInvestigation",
                   "Implementation", "Evaluation", "CommunicationAndClosure"]),
        # M2: Knowledge
        ("InterdisciplinaryBridge", ["AnalogyBridge", "MappingBridge",
                                      "InheritanceBridge", "IntegrationBridge"]),        # M3: Process
        ("ReflectionLevel", ["HabitualAction", "Understanding",
                            "CriticalReflection", "TransformativeReflection"]),
        ("IterationOutcome", ["Success", "PartialSuccess", "Failure"]),
        (("DiscourseAction"), ["HelpSeeking", "FailureReporting", "PeerArgumentation",
                            "ProcessConfusion", "KnowledgeSharing", "PlanningUtterance",
                            "IdeaGeneration", "Demonstration", "PeerEncouragement",
                            "EmotiveExpression", "SerendipitousDiscovery",
                            "HypothesisProposing", "EvidenceAnalyzing", "PrincipleFormulating",
                             "SocialBonding", "Agreement", "Disagreement",
                             "ClarificationQuestioning", "Summarizing", "TaskManagement",
                             "PeerTutoring", "CognitiveConflict", "TaskCoordination", "PeerAssessment",
                             "DesignJustification", "ConstraintReasoningAction"]),
        (("NonverbalAction"), ["PhysicalPrototyping", "ToolSharing",
                             "GazingAtPeerWork", "IdleBehavior",
                             "CelebrationGesture", "MaterialHoarding",
                              "Gesturing", "Nodding", "FacialExpression", "WritingActivity"]),
        # M4: Team
        ("Actor", ["HumanActor", "VirtualAgent"]),
        ("HumanActor", ["Learner", "Instructor"]),
        ("VirtualAgent", ["ProceduralGuide", "ConceptualExpert",
                         "MetacognitiveChallenger", "DivergentBrainstormer", "SafetyMonitor", "AffectiveSupporter"]),
        ("InstructorIntervention", ["SafetyIntervention", "DirectionalGuidance",
                                     "DeepQuestioning", "EmotionalSupport",
                                     "ClassroomManagement", "TimeManagement"]),
        # M5: Anchor
        ("CompetencyDimension", ["EngineeringThinking", "CollaborativeTeamwork",
                                 "InterdisciplinaryIntegration",
                                 "CreativityAndInnovation", "MetacognitiveSelfRegulation"]),
        ("InterdisciplinaryIntegration", ["CrossDomainConceptRecognition",
                                           "AnalogicalTransfer", "IntegratedExplanation"]),
        ("AnalyticsIndicator", ["ProcessIndicator", "CollaborationIndicator",
                                "OutcomeIndicator"]),
    ]

    for parent_name, sub_names in covering_pairs:
        parent = getattr(C, parent_name, None)
        if parent is None:
            report.append({"axiom": parent_name, "status": "MISSING_PARENT",
                          "detail": f"Class '{parent_name}' not found in registry"})
            continue

        subs = []
        for sn in sub_names:
            sc = getattr(C, sn, None)
            if sc is not None:
                subs.append(sc)

        if len(subs) != len(sub_names):
            missing = set(sub_names) - {s.name for s in subs}
            report.append({"axiom": parent_name, "status": "MISSING_SUBCLASSES",
                          "detail": f"Missing: {missing}"})
            continue

        # Verify all subs are actually subclasses
        for sc in subs:
            if parent not in sc.is_a and parent not in [x for x in sc.is_a
                                                         if isinstance(x, ThingClass)]:
                report.append({"axiom": parent_name, "status": "NOT_SUBCLASS",
                              "detail": f"{sc.name} is not a subclass of {parent_name}"})

        if not any(r["axiom"] == parent_name for r in report):
            report.append({"axiom": parent_name, "status": "OK",
                          "detail": f"{len(subs)} subclasses"})

    return report


def check_inverse_pairs(C):
    """Verify all property pairs have correct inverse linkage."""
    report = []
    # Map of expected inverse pairs
    inverse_pairs = [
        ("hasPhase", "isPhaseOf"),
        ("hasActivity", "belongsToPhase"),
        ("hasDeliverable", "isDeliverableOf"),
        ("hasConstraint", "isConstraintOf"),
        ("precedes", "succeeds"),
        ("dependsOn", "isPrerequisiteFor"),
        ("bridgesDomain", "isBridgedBy"),
        ("hasPrerequisite", "isPrerequisiteOf"),
        ("hasIteration", "isIterationOf"),
        ("hasReflection", "isReflectionOf"),
        ("hasReflectionLevel", "isLevelOfReflection"),
        ("occursInPhase", "containsDiscourse"),
        ("isFollowedByAction", "isPrecededByAction"),
        ("isTriggeredBy", "triggersAction"),
        ("iterationTriggeredBy", "triggersIteration"),
        ("hasIterationOutcome", "isOutcomeOfIteration"),
        ("referencesConcept", "isReferencedByAction"),
        ("isAttributedTo", "hasDiscourseAction"),
        ("hasTeam", "isTeamOf"),
        ("hasTeamMember", "isMemberOf"),
        ("monitorsTeam", "isMonitoredByAgent"),
        ("playsRole", "isPlayedBy"),
        ("hasDomainBoundary", "isDomainOfAgent"),
        ("triggersAgent", "isTriggeredByDiscourse"),
        ("tracesCompetency", "isTracedByPerformance"),
        ("hasPerformanceTrace", "isGeneratedByLearner"),
        ("hasCompetencyProfile", "isProfileOf"),
        ("aggregatesTrace", "isAggregatedIn"),
        ("derivedFromEvent", "generatesTrace"),
        ("hasTeamState", "isStateOfTeam"),
        ("hasAnalyticsIndicator", "isIndicatorOfState"),
        ("linksConcept", "isLinkedByBridge"),
        ("requiresConcept", "isConceptRequiredBy"),
        ("generatedInActivity", "generatesBridge"),
        ("belongsToDomain", "includesConcept"),
        ("isAppliedInActivity", "appliesConcept"),
        ("occursWithinProcess", "hasIterationEvent"),
        # v2.1 new pairs
        ("justifiesDecision", "isDecisionJustifiedBy"),
        ("instructsTeam", "isInstructedBy"),
        ("speaksTo", "isSpokenToBy"),
        ("respondsTo", "isRespondedToBy"),
        ("sharesWith", "isSharedWithBy"),
        ("hasCognitiveStep", "isCognitiveStepOf"),
        ("evidencesCompetency", "isEvidencedBy"),
        ("hasAlignment", "isAlignmentOf"),
        # v3.0
        ("hasSubPhase", "isSubPhaseOf"),
        ("isProducedBy", "producesDeliverable"),
        ("constraintViolationTriggers", "isTriggeredByConstraint"),
        ("expressesPerspective", "isExpressedInAction"),
        ("directedToTeam", "isTargetedByAction"),
        ("referencesTeamWork", "isReferencedByTeam"),
    ]

    for fwd_name, rev_name in inverse_pairs:
        fwd = getattr(C, fwd_name, None)
        rev = getattr(C, rev_name, None)

        if fwd is None:
            report.append({"pair": f"{fwd_name}/{rev_name}", "status": "MISSING_FWD"})
            continue
        if rev is None:
            report.append({"pair": f"{fwd_name}/{rev_name}", "status": "MISSING_REV"})
            continue

        actual_inv = fwd.inverse_property
        if actual_inv is None:
            report.append({"pair": f"{fwd_name}/{rev_name}", "status": "NO_INVERSE"})
        elif actual_inv.name != rev_name:
            report.append({"pair": f"{fwd_name}/{rev_name}", "status": "WRONG_INVERSE",
                          "detail": f"Expected {rev_name}, got {actual_inv.name}"})
        else:
            report.append({"pair": f"{fwd_name}/{rev_name}", "status": "OK"})

    return report


def main():
    json_mode = "--json" in sys.argv

    # Build TBox
    C = build_all_tbox()

    results = {
        "consistency": "UNKNOWN",
        "covering_axioms": [],
        "inverse_pairs": [],
        "errors": [],
    }

    # 1. Pellet consistency
    ok = validate_with_pellet()
    results["consistency"] = "CONSISTENT" if ok else "INCONSISTENT"
    if not ok:
        results["errors"].append("Pellet reasoner reported inconsistency")

    # 2. Covering axioms
    results["covering_axioms"] = check_covering_axioms(C)
    for r in results["covering_axioms"]:
        if r["status"] != "OK":
            results["errors"].append(f"Covering: {r}")

    # 3. Inverse pairs
    results["inverse_pairs"] = check_inverse_pairs(C)
    for r in results["inverse_pairs"]:
        if r["status"] != "OK":
            results["errors"].append(f"Inverse: {r}")

    # 4. Stats
    world = default_world
    results["stats"] = {
        "classes": len(list(world.classes())),
        "object_properties": len(list(world.object_properties())),
        "data_properties": len(list(world.data_properties())),
        "individuals": len(list(world.individuals())),
    }

    if json_mode:
        print(json.dumps(results, indent=2))
    else:
        print("\n" + "=" * 60)
        print("VALIDATION REPORT")
        print("=" * 60)

        print(f"\nConsistency: {results['consistency']}")

        n_ok = sum(1 for r in results["covering_axioms"] if r["status"] == "OK")
        n_total = len(results["covering_axioms"])
        print(f"\nCovering Axioms: {n_ok}/{n_total}")
        for r in results["covering_axioms"]:
            status_icon = "✓" if r["status"] == "OK" else "✗"
            print(f"  {status_icon} {r['axiom']}: {r['status']}")

        n_ok = sum(1 for r in results["inverse_pairs"] if r["status"] == "OK")
        n_total = len(results["inverse_pairs"])
        print(f"\nInverse Pairs: {n_ok}/{n_total}")
        for r in results["inverse_pairs"]:
            if r["status"] != "OK":
                print(f"  ✗ {r['pair']}: {r['status']}")

        print(f"\nStats: {results['stats']}")

        if not results["errors"]:
            print("\n✅ ALL VALIDATION CHECKS PASSED")
        else:
            print(f"\n❌ {len(results['errors'])} ERRORS FOUND")

    return 0 if not results["errors"] else 1


if __name__ == "__main__":
    sys.exit(main())
