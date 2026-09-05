#!/usr/bin/env python3
"""
tbox.py — SINGLE SOURCE OF TRUTH for the IE-PBL Ontology TBox.

All five modules are defined here as functions. Each function builds the module
in the shared default_world. Export is handled separately by export_modules().

Usage:
    from tbox import build_all_tbox, export_modules

    classes = build_all_tbox()
    export_modules()                    # writes 5 .ttl files
    export_ie_pbl_master(classes)       # writes ie-pbl.ttl with owl:imports

Design principles:
  - DRY: each class/property defined exactly once
  - Uses owl_helpers factory functions to eliminate boilerplate
  - Cross-module references use Python object references (shared World)
  - Serialization: partition by namespace on export (not during build)
"""

import sys
import os
import datetime as dt

# Ensure owlready2 is on the path (handles both dev and installed contexts)
_venv_site = os.path.join(os.path.dirname(__file__), "..", ".venv", "lib")
if os.path.isdir(_venv_site):
    for _pyver in ["python3.9", "python3.10", "python3.11", "python3.12"]:
        _sp = os.path.join(_venv_site, _pyver, "site-packages")
        if os.path.isdir(_sp):
            sys.path.insert(0, _sp)
            break

from owlready2 import *
from config import IRI, MODULE_IRIS, MODULE_PATHS
from owl_helpers import (
    make_class, make_property_pair, make_datatype_prop,
    declare_covering, declare_disjoint,
)


# ═══════════════════════════════════════════════════════════════════════════════
# TBox CLASS REGISTRY — populated by build functions
# ═══════════════════════════════════════════════════════════════════════════════

class TBClasses:
    """Holds references to all ontology classes, organized by module."""
    pass

C = TBClasses()  # global registry — populated as modules are built


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE 1: CORE
# ═══════════════════════════════════════════════════════════════════════════════

def build_core():
    """Build Module 1: Core — Projects, Phases, Activities."""
    onto = get_ontology(MODULE_IRIS["core"])

    with onto:
        # ── Classes ──
        C.Project = make_class(onto, "Project",
            comment="A PBL unit consisting of phases, activities, constraints, and deliverables.")
        C.Phase = make_class(onto, "Phase",
            comment="A temporal segment of a project (e.g. Ask, Imagine, Plan, Create, Improve).")
        C.Activity = make_class(onto, "Activity",
            comment="An atomic learning task within a phase.")
        C.Constraint = make_class(onto, "Constraint",
            comment="A boundary condition on a project (time, resource, scope, etc.).")
        C.Deliverable = make_class(onto, "Deliverable",
            comment="A tangible output artifact produced by an activity.")

        # Gold Standard PBL elements (Larmer & Mergendoller, 2015)
        C.DrivingQuestion = make_class(onto, "DrivingQuestion",
            comment="The central, open-ended question that drives the PBL project inquiry.")
        C.EntryEvent = make_class(onto, "EntryEvent", bases=(C.Activity,),
            comment="The initial hook activity that introduces the project and sparks curiosity.")

        # ═══════════════════════════════════════════════════════════════
        # TWO-TIERED PHASE TAXONOMY
        #
        # Tier 1: Generic Macro-Phases (top-level subclasses of Phase).
        #   These are the targets for SWRL rules — framework-agnostic.
        # Tier 2: Framework-Specific Subclasses (subclasses of Macro-Phases).
        #   EiE for K-8, CDIO for higher-ed. Pellet subsumption reasoning
        #   automatically infers that any framework-specific phase subsumes to
        #   its macro-phase parent (e.g. EiE_Create ⊑ Implementation at deployment).
        #
        # References:
        #   EiE: Engineering is Elementary (Boston Museum of Science)
        #   CDIO: Crawley et al. (2007), adopted by 160+ universities
        #   NGSS: Science & Engineering Practices (NRC, 2012)
        # ═══════════════════════════════════════════════════════════════

        # ── Tier 1: Generic Macro-Phases ──
        C.ProblemScoping = make_class(onto, "ProblemScoping", bases=(C.Phase,),
            comment="Defining the problem space, identifying constraints, establishing success criteria.")
        C.SolutionIdeation = make_class(onto, "SolutionIdeation", bases=(C.Phase,),
            comment="Generating, brainstorming, and selecting among possible solutions.")
        C.ScientificInvestigation = make_class(onto, "ScientificInvestigation", bases=(C.Phase,),
            comment="Formal scientific inquiry: experiments, data analysis, and discovery of laws "
                    "that inform engineering design. Key to Integrated STEM 'Informed Design' (Burghardt & Hacker, 2004).")
        C.Implementation = make_class(onto, "Implementation", bases=(C.Phase,),
            comment="Building, coding, prototyping — translating design into artifact.")
        C.Evaluation = make_class(onto, "Evaluation", bases=(C.Phase,),
            comment="Testing, measuring, analyzing results against criteria, iterating.")
        C.CommunicationAndClosure = make_class(onto, "CommunicationAndClosure", bases=(C.Phase,),
            comment="Presenting outcomes, documenting processes, reflecting, closing the project.")

        # Macro-Phases are pairwise disjoint (now 6)
        declare_disjoint(C.ProblemScoping, C.SolutionIdeation, C.ScientificInvestigation,
                         C.Implementation, C.Evaluation, C.CommunicationAndClosure)
        declare_covering(C.Phase, [C.ProblemScoping, C.SolutionIdeation, C.ScientificInvestigation,
                                    C.Implementation, C.Evaluation, C.CommunicationAndClosure])

        # ── Tier 2: Closure Sub-Phases (Gold Standard PBL) ──
        # The only macro-phase without EDP-framework coverage; its internal
        # structure comes from PBL pedagogy (Larmer et al. 2015).
        # Other frameworks (EiE, CDIO, 5E) are discussed in the paper as
        # examples of subsumption but are not pre-defined in the base ontology;
        # they are added as Tier-2 subclasses at deployment time.

        C.PresentationRehearsal = make_class(onto, "PresentationRehearsal", bases=(C.CommunicationAndClosure,),
            comment="[GSPBL: critique & revision] Preparing and rehearsing the public presentation: "
                    "drafting slides, practicing delivery, peer critique before the audience session.")
        C.FinalPresentation = make_class(onto, "FinalPresentation", bases=(C.CommunicationAndClosure,),
            comment="[GSPBL: public product] Final public presentation of the project outcomes "
                    "to an audience beyond the team.")
        C.ClosingCeremony = make_class(onto, "ClosingCeremony", bases=(C.CommunicationAndClosure,),
            comment="[GSPBL: public product] Ceremonial closing of the project: guest speeches, "
                    "awards where given, group photos, and farewell; not all projects include awards.")

        declare_disjoint(C.PresentationRehearsal, C.FinalPresentation, C.ClosingCeremony)

        # ── Activity Subtypes: Distinguishing Inquiry from Design from Making ──
        # Reference: Informed Design (Burghardt & Hacker, 2004); NGSS Science & Engineering Practices
        C.DesignActivity = make_class(onto, "DesignActivity", bases=(C.Activity,),
            comment="Cognitive design work: sketching, CAD modeling, calculating, planning.")
        C.MakingActivity = make_class(onto, "MakingActivity", bases=(C.Activity,),
            comment="Physical fabrication: 3D printing, assembling, cutting, soldering.")
        C.InquiryActivity = make_class(onto, "InquiryActivity", bases=(C.Activity,),
            comment="Scientific investigation: conducting experiments, collecting data, reviewing literature.")
        declare_disjoint(C.DesignActivity, C.MakingActivity, C.InquiryActivity)

        # Disjointness — top-level Core classes
        declare_disjoint(C.Project, C.Phase, C.Activity, C.Constraint, C.Deliverable,
                         C.DrivingQuestion)

        # ── Object Properties ──
        C.hasPhase, C.isPhaseOf = make_property_pair(onto,
            "hasPhase", "isPhaseOf", C.Project, C.Phase)
        C.hasActivity, C.belongsToPhase = make_property_pair(onto,
            "hasActivity", "belongsToPhase", C.Phase, C.Activity)
        C.hasDeliverable, C.isDeliverableOf = make_property_pair(onto,
            "hasDeliverable", "isDeliverableOf", C.Activity, C.Deliverable)
        C.hasConstraint, C.isConstraintOf = make_property_pair(onto,
            "hasConstraint", "isConstraintOf", C.Project, C.Constraint)
        C.precedes, C.succeeds = make_property_pair(onto,
            "precedes", "succeeds", C.Phase, C.Phase, transitive=True)
        C.dependsOn, C.isPrerequisiteFor = make_property_pair(onto,
            "dependsOn", "isPrerequisiteFor", C.Activity, C.Activity)

        C.precedes.comment.append("Temporal ordering between phases. Transitive.@en")
        C.dependsOn.comment.append("Prerequisite dependency between activities.@en")

        # Driving Question link
        C.hasDrivingQuestion, C.isDrivingQuestionOf = make_property_pair(onto,
            "hasDrivingQuestion", "isDrivingQuestionOf", C.Project, C.DrivingQuestion)

        # Nonlinear phase navigation (addressing teacher review — real classrooms are messy)
        C.backtracksTo, C.isBacktrackedFrom = make_property_pair(onto,
            "backtracksTo", "isBacktrackedFrom", C.Phase, C.Phase)
        C.backtracksTo.comment.append(
            "Indicates a recursive backtrack from one phase to a prior phase. "
            "Non-transitive — models real design process recursion.@en")

        C.concurrentWith = type("concurrentWith", (SymmetricProperty, ObjectProperty), {"namespace": onto})
        C.concurrentWith.label.append("concurrent with@en")
        C.concurrentWith.comment.append(
            "Two phases that occur simultaneously. Symmetric. Models real classrooms "
            "where Create and Improve often happen concurrently.@en")
        C.concurrentWith.domain.append(C.Phase)
        C.concurrentWith.range.append(C.Phase)

        # ── Data Properties ──
        C.hasTitle = make_datatype_prop(onto, "hasTitle", [Thing], str)
        C.hasDescription = make_datatype_prop(onto, "hasDescription", [Thing], str)
        C.questionText = make_datatype_prop(onto, "questionText", [C.DrivingQuestion], str)
        C.questionText.comment.append("The text of a driving question.@en")
        C.startTime = make_datatype_prop(onto, "startTime", [Or([C.Project, C.Phase])], dt.datetime)
        C.endTime = make_datatype_prop(onto, "endTime", [Or([C.Project, C.Phase])], dt.datetime)
        # Cognitive mode for phases: 'divergent' vs 'convergent' thinking
        C.hasCognitiveMode = make_datatype_prop(onto, "hasCognitiveMode", [C.SolutionIdeation], str)
        C.hasCognitiveMode.comment.append(
            "Cognitive mode of a SolutionIdeation phase: 'divergent' (brainstorming, "
            "generating alternatives) or 'convergent' (selecting, refining, planning).@en")

        # ── v3.0: SubPhase — finer-grained decomposition of Phase ──
        # Allows different grade bands to have different internal phase structure
        # without modifying the abstract Phase taxonomy.
        C.SubPhase = make_class(onto, "SubPhase",
            comment="A finer-grained sub-stage within a Phase. Allows grade-band-specific "
                    "decomposition without modifying the abstract Phase taxonomy. "
                    "Example: ProblemScoping may decompose into NeedsFinding, StakeholderAnalysis, "
                    "ConstraintIdentification for high school, but remain undivided for K-2.")
        C.hasSubPhase, C.isSubPhaseOf = make_property_pair(onto,
            "hasSubPhase", "isSubPhaseOf", C.Phase, C.SubPhase)

        # ── v3.0: Deliverable hooks — minimal structural mount points for future
        # quality assessment systems (decoupled from base ontology) ──
        C.deliverableType = make_datatype_prop(onto, "deliverableType", [C.Deliverable], str)
        C.deliverableType.comment.append(
            "Type of deliverable: 'prototype', 'report', 'presentation', 'code', "
            "'model', 'artifact', 'poster', 'video'. Enables filtering before "
            "quality assessment plugin is loaded.@en")
        C.isProducedBy, C.producesDeliverable = make_property_pair(onto,
            "isProducedBy", "producesDeliverable", C.Deliverable, Thing)  # range tightened to Learner in M4
        C.isProducedBy.comment.append(
            "The learner who produced this deliverable. Links artifact to creator "
            "for per-student quality assessment.@en")
        C.hasEvaluationCriterion = make_datatype_prop(onto, "hasEvaluationCriterion", [C.Deliverable], str)
        C.hasEvaluationCriterion.comment.append(
            "External rubric item reference (ID or URL). Decoupled hook for future "
            "quality assessment plugin. Example: 'rubric.creativity', 'ngss.hs-ets1-2'.@en")

        # ── v3.0: Constraint dynamic reasoning — captures constraint-driven design backtracking ──
        C.constraintViolationTriggers, C.isTriggeredByConstraint = make_property_pair(onto,
            "constraintViolationTriggers", "isTriggeredByConstraint", C.Constraint, C.Phase)
        C.constraintViolationTriggers.comment.append(
            "A constraint violation triggers backtracking to a prior phase. "
            "Captures the dynamic 'constraint conflict → redesign' pattern in real PBL.@en")

    print(f"  ✓ M1 Core: {_count(onto, 'classes')} classes, {_count(onto, 'object_properties')} obj props, {_count(onto, 'data_properties')} data props")
    return onto


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE 2: KNOWLEDGE
# ═══════════════════════════════════════════════════════════════════════════════

def build_knowledge():
    """Build Module 2: Knowledge — Concepts, Skills, Interdisciplinary Bridges."""
    onto = get_ontology(MODULE_IRIS["knowledge"])

    with onto:
        # ── Classes ──
        C.Concept = make_class(onto, "Concept",
            comment="A domain concept (e.g. Bernoulli's Principle, Torque).")
        C.Skill = make_class(onto, "Skill",
            comment="A procedural capability (e.g. CAD Modeling, Data Analysis).")
        C.DomainBoundary = make_class(onto, "DomainBoundary",
            comment="Marks the epistemological scope of a domain (e.g. Physics, Engineering).")
        C.InterdisciplinaryBridge = make_class(onto, "InterdisciplinaryBridge",
            comment="Abstract top class for interdisciplinary connections (Klein).")

        # Klein's taxonomy subclasses
        C.AnalogyBridge = make_class(onto, "AnalogyBridge", bases=(C.InterdisciplinaryBridge,))
        C.MappingBridge = make_class(onto, "MappingBridge", bases=(C.InterdisciplinaryBridge,))
        C.InheritanceBridge = make_class(onto, "InheritanceBridge", bases=(C.InterdisciplinaryBridge,))
        C.IntegrationBridge = make_class(onto, "IntegrationBridge", bases=(C.InterdisciplinaryBridge,))

        # Boundary Crossing (Akkerman & Bakker, 2011)
        # v4.0: the four dialogical mechanisms restored as classes — they are
        # mechanisms (they can co-occur and recur), not developmental stages of
        # an artifact. They are enacted by reified BoundaryCrossingEvent
        # individuals rather than attached to bridges as a datatype property.
        C.BoundaryCrossingMechanism = make_class(onto, "BoundaryCrossingMechanism",
            comment="Abstract parent of Akkerman & Bakker's (2011) four dialogical "
                    "boundary-crossing mechanisms.@en")
        C.IdentificationMechanism = make_class(onto, "IdentificationMechanism", bases=(C.BoundaryCrossingMechanism,),
            comment="Recognizing differences between practices and identifying one's "
                    "own position relative to them.@en")
        C.CoordinationMechanism = make_class(onto, "CoordinationMechanism", bases=(C.BoundaryCrossingMechanism,),
            comment="Establishing and using translation or synchronization procedures "
                    "between two practices.@en")
        C.ReflectionMechanism = make_class(onto, "ReflectionMechanism", bases=(C.BoundaryCrossingMechanism,),
            comment="Explicit perspective-taking and comparison between practices, "
                    "often jointly with boundary objects.@en")
        C.TransformationMechanism = make_class(onto, "TransformationMechanism", bases=(C.BoundaryCrossingMechanism,),
            comment="Developing hybrid practices that combine learning from both "
                    "sides of the boundary.@en")
        declare_disjoint(C.IdentificationMechanism, C.CoordinationMechanism,
                         C.ReflectionMechanism, C.TransformationMechanism)
        declare_covering(C.BoundaryCrossingMechanism,
            [C.IdentificationMechanism, C.CoordinationMechanism,
             C.ReflectionMechanism, C.TransformationMechanism])

        # v4.0: reified crossing episode — one event may enact several mechanisms
        # (co-occurrence), and events may recur for the same bridge (recurrence).
        C.BoundaryCrossingEvent = make_class(onto, "BoundaryCrossingEvent",
            comment="An observable boundary-crossing episode enacted by one or more "
                    "dialogical mechanisms (Akkerman & Bakker, 2011).@en")

        declare_disjoint(C.AnalogyBridge, C.MappingBridge, C.InheritanceBridge, C.IntegrationBridge)
        declare_covering(C.InterdisciplinaryBridge,
            [C.AnalogyBridge, C.MappingBridge, C.InheritanceBridge, C.IntegrationBridge])

        # ── v3.0: ValuePerspective — non-cognitive knowledge for humanities/social science PBL ──
        C.ValuePerspective = make_class(onto, "ValuePerspective",
            comment="A stakeholder value, normative perspective, ethical consideration, "
                    "or empathic understanding. Extends the knowledge model beyond "
                    "cognitive propositional knowledge (Concept) and procedural "
                    "knowledge (Skill) to include affective and normative dimensions "
                    "essential for socio-scientific PBL projects.@en")

        declare_disjoint(C.Concept, C.Skill, C.DomainBoundary, C.InterdisciplinaryBridge, C.BoundaryCrossingEvent, C.BoundaryCrossingMechanism, C.ValuePerspective)

        # ── Object Properties ──
        C.bridgesDomain, C.isBridgedBy = make_property_pair(onto,
            "bridgesDomain", "isBridgedBy", C.InterdisciplinaryBridge, C.DomainBoundary)
        C.InterdisciplinaryBridge.is_a.append(C.bridgesDomain.min(2, C.DomainBoundary))

        C.linksConcept, C.isLinkedByBridge = make_property_pair(onto,
            "linksConcept", "isLinkedByBridge", C.InterdisciplinaryBridge, C.Concept)

        # v4.0: mechanisms attach to reified crossing events, not to bridges.
        C.crossesBridge, C.hasCrossingEvent = make_property_pair(onto,
            "crossesBridge", "hasCrossingEvent", C.BoundaryCrossingEvent, C.InterdisciplinaryBridge)
        C.enactsMechanism, C.mechanismEnactedIn = make_property_pair(onto,
            "enactsMechanism", "mechanismEnactedIn", C.BoundaryCrossingEvent, C.BoundaryCrossingMechanism)
        C.BoundaryCrossingEvent.is_a.append(C.enactsMechanism.min(1, C.BoundaryCrossingMechanism))

        C.requiresConcept, C.isConceptRequiredBy = make_property_pair(onto,
            "requiresConcept", "isConceptRequiredBy", C.Skill, C.Concept)
        C.requiresConcept.comment.append(
            "A Skill depends on a Concept (e.g. CAD Modeling requires Spatial Geometry).@en")

        # Cross-module: Bridge → Activity (M1)
        C.generatedInActivity, C.generatesBridge = make_property_pair(onto,
            "generatedInActivity", "generatesBridge", C.InterdisciplinaryBridge, C.Activity)
        C.generatedInActivity.comment.append(
            "Links a bridge to the Activity where interdisciplinary thinking emerged.@en")

        C.belongsToDomain, C.includesConcept = make_property_pair(onto,
            "belongsToDomain", "includesConcept",
            Or([C.Concept, C.Skill]), C.DomainBoundary)

        C.hasPrerequisite, C.isPrerequisiteOf = make_property_pair(onto,
            "hasPrerequisite", "isPrerequisiteOf",
            Or([C.Concept, C.Skill]), Or([C.Concept, C.Skill]))
        C.hasPrerequisite.comment.append(
            "Knowledge prerequisite. Distinct from Activity-level dependsOn.@en")

        # Cross-module: Concept/Skill → Activity (M1)
        C.isAppliedInActivity, C.appliesConcept = make_property_pair(onto,
            "isAppliedInActivity", "appliesConcept",
            Or([C.Concept, C.Skill]), C.Activity)

        # ── Data Properties ──
        C.hasDefinition = make_datatype_prop(onto, "hasDefinition", [C.Concept], str)
        C.hasDefinition.comment.append("Formal academic definition of a Concept.@en")
        C.hasProficiencyLevel = make_datatype_prop(onto, "hasProficiencyLevel", [C.Skill], int)
        C.hasIntegrationDepth = make_datatype_prop(onto, "hasIntegrationDepth", [C.InterdisciplinaryBridge], int)
        C.hasIntegrationDepth.comment.append(
            "Depth of interdisciplinary integration on a 1-5 Likert scale. "
            "1=superficial awareness; 3=moderate synthesis; 5=deep transformation.@en")

        # v4.0: crossing events are timestamped so mechanism recurrence can be
        # analyzed over time without re-typing artifacts.
        C.crossingTimestamp = make_datatype_prop(onto, "crossingTimestamp", [C.BoundaryCrossingEvent], str)
        C.crossingTimestamp.comment.append(
            "When this boundary-crossing episode occurred (ISO 8601).@en")

        # v3.0: Bridge complexity for multi-domain projects
        C.bridgeComplexity = make_datatype_prop(onto, "bridgeComplexity", [C.InterdisciplinaryBridge], int)
        C.bridgeComplexity.comment.append(
            "Number of domains this bridge spans. 2=binary bridge, 3+=complex "
            "multi-domain integration. Enables differentiation between simple "
            "cross-domain links and complex synthesis in projects with 4+ disciplines.@en")

        # v3.0: ValuePerspective links
        C.expressesPerspective, C.isExpressedInAction = make_property_pair(onto,
            "expressesPerspective", "isExpressedInAction", Thing, C.ValuePerspective)
        C.expressesPerspective.comment.append(
            "Links a discourse action (or activity) to the value perspective it expresses. "
            "Domain tightened to DiscourseAction in M3.@en")

        # ── PROV-O Alignment ──
        # The IE-PBL Ontology aligns with the W3C PROV-O standard (https://www.w3.org/TR/prov-o/)
        # for provenance tracking. The wasDerivedFrom annotation property provides a standard
        # mapping between PROV-O provenance concepts and our derivedFromEvent (Module 5).
        #   PROV-O wasDerivedFrom ←→ IE-PBL derivedFromEvent (PerformanceTrace provenance chain)
        C.wasDerivedFrom = type("wasDerivedFrom", (AnnotationProperty,), {"namespace": onto})
        C.wasDerivedFrom.label.append("was derived from@en")
        C.wasDerivedFrom.comment.append(
            "PROV-O alignment: standard provenance mapping. Corresponds to PROV-O wasDerivedFrom. "
            "In IE-PBL, the primary provenance chain uses derivedFromEvent (Module 5) to anchor "
            "PerformanceTraces to originating PBL events.@en")

    print(f"  ✓ M2 Knowledge: {_count(onto, 'classes')} classes, {_count(onto, 'object_properties')} obj props, {_count(onto, 'data_properties')} data props")
    return onto


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE 3: PROCESS & DISCOURSE
# ═══════════════════════════════════════════════════════════════════════════════

def build_process():
    """Build Module 3: Process & Discourse — EDP, Iterations, DiscourseActions."""
    onto = get_ontology(MODULE_IRIS["process"])

    with onto:
        # ── LearningEvent (abstract root for all observable events) ──
        # v3.1: moved back to M3 (its conceptual home, the event layer).
        # v3.0 had placed it in Core to resolve an M3↔M4 import cycle; that
        # cycle no longer exists (M4 already references M3 classes, and
        # isAttributedTo uses the placeholder-range + M5 refinement pattern).
        # DiscourseAction, NonverbalAction (M3), and InstructorIntervention (M4)
        # all extend this class; extension point for future event types
        # (e.g. AILearningEvent).
        C.LearningEvent = make_class(onto, "LearningEvent",
            comment="Abstract parent for all observable learning behaviors (verbal and nonverbal).")
        C.hasModality = make_datatype_prop(onto, "hasModality", [C.LearningEvent], str)
        C.hasModality.comment.append(
            "Communication modality of a learning event: 'verbal', 'gestural', "
            "'physical', 'written', 'digital', 'facial'. Supports multi-modal learning analytics.@en")

        # ── Core Process Classes ──
        C.Iteration = make_class(onto, "Iteration",
            comment="A single design cycle within an engineering design process.")
        # v4.1: Reflection is a product, not an event. It carries the
        # reflection text and its Kember depth level, while the observable
        # events that express it live in the LearningEvent hierarchy and
        # link to it via expressesReflection (attribution and timing on
        # the event; the product stays time-invariant).
        C.Reflection = make_class(onto, "Reflection",
            comment="A reflection product — e.g. a written journal entry or "
                    "recorded reflective artifact — capturing metacognitive "
                    "reflection on process or learning. Modeled as a product "
                    "rather than an event: it carries the reflection text and "
                    "its Kember depth level, while the observable events that "
                    "express it are LearningEvent individuals linked via "
                    "expressesReflection.")

        # ── Reflection Levels (Kember et al., 2008) ──
        C.ReflectionLevel = make_class(onto, "ReflectionLevel",
            comment="Depth of reflection per Kember et al. (2008) framework.")
        C.HabitualAction = make_class(onto, "HabitualAction", bases=(C.ReflectionLevel,),
            comment="Non-reflective, routine action without conscious thought.")
        C.Understanding = make_class(onto, "Understanding", bases=(C.ReflectionLevel,),
            comment="Intentional learning: constructing meaning without critique "
                    "of premises.")
        C.ReflectiveThought = make_class(onto, "ReflectiveThought", bases=(C.ReflectionLevel,),
            comment="Kember's 'reflection' level: conscious, deliberate examination "
                    "of experience and knowledge to guide action. Encoded as "
                    "ReflectiveThought to avoid a name clash with the M3 "
                    "Reflection activity class.@en")
        C.CriticalReflection = make_class(onto, "CriticalReflection", bases=(C.ReflectionLevel,),
            comment="Premise critique: reflection directed at the assumptions "
                    "underlying beliefs and actions (Kember et al., 2008).")
        declare_disjoint(C.HabitualAction, C.Understanding, C.ReflectiveThought, C.CriticalReflection)
        declare_covering(C.ReflectionLevel,
            [C.HabitualAction, C.Understanding, C.ReflectiveThought, C.CriticalReflection])

        # ── Iteration Outcomes ──
        C.IterationOutcome = make_class(onto, "IterationOutcome",
            comment="The result of an engineering design iteration.")
        C.Success = make_class(onto, "Success", bases=(C.IterationOutcome,),
            comment="The iteration met all success criteria.")
        C.PartialSuccess = make_class(onto, "PartialSuccess", bases=(C.IterationOutcome,),
            comment="The iteration met some but not all success criteria.")
        C.Failure = make_class(onto, "Failure", bases=(C.IterationOutcome,),
            comment="The iteration failed to meet success criteria.")
        declare_disjoint(C.Success, C.PartialSuccess, C.Failure)
        declare_covering(C.IterationOutcome, [C.Success, C.PartialSuccess, C.Failure])

        # ── Discourse Actions ──
        # v3.0: Two-tier taxonomy with 6 intermediate categories.
        # Enables SWRL rules to target categories (e.g. ScientificInquiryAction)
        # instead of enumerating individual leaf types.
        C.DiscourseAction = make_class(onto, "DiscourseAction",
            comment="Micro-level communicative intent capturing granular student discourse.")

        # ── Tier 1.5: Intermediate Discourse Categories (v3.0) ──
        C.ScientificInquiryAction = make_class(onto, "ScientificInquiryAction", bases=(C.DiscourseAction,),
            comment="Scientific reasoning: proposing hypotheses, analyzing evidence, formulating principles.")
        C.DesignReasoningAction = make_class(onto, "DesignReasoningAction", bases=(C.DiscourseAction,),
            comment="Design thinking: ideation, planning, evidence-based justification.")
        C.CollaborativeDiscourseAction = make_class(onto, "CollaborativeDiscourseAction", bases=(C.DiscourseAction,),
            comment="Peer collaboration: argumentation, tutoring, assessment, coordination, knowledge sharing.")
        C.HelpSeekingAction = make_class(onto, "HelpSeekingAction", bases=(C.DiscourseAction,),
            comment="Help-seeking and confusion expression: requests for help, process confusion, clarification, failure reporting.")
        C.SocialAffectiveAction = make_class(onto, "SocialAffectiveAction", bases=(C.DiscourseAction,),
            comment="Social and affective expression: bonding, agreement/disagreement, encouragement, emotion.")
        C.RegulatoryAction = make_class(onto, "RegulatoryAction", bases=(C.DiscourseAction,),
            comment="Metacognitive regulation: summarizing, task management, demonstration, serendipitous discovery, reflective expression.")

        # --- Existing 14 types ---
        C.HelpSeeking = make_class(onto, "HelpSeeking", bases=(C.HelpSeekingAction,),
            comment="Student requests procedural or conceptual assistance (Hannafin).")
        C.FailureReporting = make_class(onto, "FailureReporting", bases=(C.HelpSeekingAction,),
            comment="Student reports a failure, unexpected result, or error.")
        C.PeerArgumentation = make_class(onto, "PeerArgumentation", bases=(C.CollaborativeDiscourseAction,),
            comment="Epistemic discourse: students argue, debate, or reason collaboratively.")
        C.ProcessConfusion = make_class(onto, "ProcessConfusion", bases=(C.HelpSeekingAction,),
            comment="Student expresses confusion about the design process itself.")
        C.KnowledgeSharing = make_class(onto, "KnowledgeSharing", bases=(C.CollaborativeDiscourseAction,),
            comment="Student proactively shares domain knowledge with peers.")
        C.PlanningUtterance = make_class(onto, "PlanningUtterance", bases=(C.DesignReasoningAction,),
            comment="Student articulates a planning or strategy statement.")
        C.IdeaGeneration = make_class(onto, "IdeaGeneration", bases=(C.DesignReasoningAction,),
            comment="Student generates novel ideas, brainstorms, or proposes hypotheses.")

        # Extended discourse types (v1.1 — from teacher/educator review)
        C.Demonstration = make_class(onto, "Demonstration", bases=(C.RegulatoryAction,),
            comment="Student showcases a result or prototype to peers or teacher.")
        C.PeerEncouragement = make_class(onto, "PeerEncouragement", bases=(C.SocialAffectiveAction,),
            comment="Student provides emotional support or encouragement to a peer.")
        C.EmotiveExpression = make_class(onto, "EmotiveExpression", bases=(C.SocialAffectiveAction,),
            comment="Student expresses emotion (frustration, excitement, disappointment) related to the task.")
        C.SerendipitousDiscovery = make_class(onto, "SerendipitousDiscovery", bases=(C.RegulatoryAction,),
            comment="Student reports an unexpected discovery or surprising result.")

        # v4.1: ReflectiveExpression — observable counterpart of the Reflection
        # product. Closes a coverage gap in the coding scheme: verbal reflection
        # is not Summarizing (which recaps discussion content, not self-evaluative
        # metacognition), and written reflection is not merely WrittenExpression
        # (a modality-level code for any writing). Links to the product via
        # expressesReflection.
        C.ReflectiveExpression = make_class(onto, "ReflectiveExpression", bases=(C.RegulatoryAction,),
            comment="Student externally expresses reflective content about their "
                    "own process or learning (e.g. 'We didn't account for torque — "
                    "next time we should test pitch angles first'), verbally or "
                    "in writing. Observable counterpart of the Reflection "
                    "product; linked to it via expressesReflection, with "
                    "attribution and timing carried by the event.")

        # ── Scientific Method Discourse Types (Informed Design / S2D) ──
        C.HypothesisProposing = make_class(onto, "HypothesisProposing", bases=(C.ScientificInquiryAction,),
            comment="Student proposes a testable scientific hypothesis (e.g. 'A steeper angle generates more voltage.').")
        C.EvidenceAnalyzing = make_class(onto, "EvidenceAnalyzing", bases=(C.ScientificInquiryAction,),
            comment="Student interprets experimental data (e.g. 'The multimeter shows a 0.3V drop at 15°.').")
        C.PrincipleFormulating = make_class(onto, "PrincipleFormulating", bases=(C.ScientificInquiryAction,),
            comment="Student synthesizes a scientific principle from evidence "
                    "(e.g. 'Efficiency stalls past the optimal pitch angle due to flow separation.'). "
                    "This is the cognitive link from Science to Design — key to the S2D Bridge.")

        # --- v2.1 NEW: Social / Affective / Regulatory discourse types ---
        C.SocialBonding = make_class(onto, "SocialBonding", bases=(C.SocialAffectiveAction,),
            comment="Social talk, joking, or humor that builds team cohesion but is off-task.")
        C.Agreement = make_class(onto, "Agreement", bases=(C.SocialAffectiveAction,),
            comment="Simple agreement or affirmation (e.g. 'Yeah, I agree', 'Good point').")
        C.Disagreement = make_class(onto, "Disagreement", bases=(C.SocialAffectiveAction,),
            comment="Simple disagreement or negation (e.g. 'I don't think so', 'No').")
        C.ClarificationQuestioning = make_class(onto, "ClarificationQuestioning", bases=(C.HelpSeekingAction,),
            comment="Student asks for clarification (distinct from HelpSeeking — not requesting help but clarification).")
        C.Summarizing = make_class(onto, "Summarizing", bases=(C.RegulatoryAction,),
            comment="Student summarizes, recaps, or synthesizes what has been discussed.")
        C.TaskManagement = make_class(onto, "TaskManagement", bases=(C.RegulatoryAction,),
            comment="Task redirection or management (e.g. 'Let's finish this part first').")

        # --- v2.1 NEW: Peer Interaction types ---
        C.PeerTutoring = make_class(onto, "PeerTutoring", bases=(C.CollaborativeDiscourseAction,),
            comment="One student explains a concept or teaches a skill to a peer.")
        C.CognitiveConflict = make_class(onto, "CognitiveConflict", bases=(C.CollaborativeDiscourseAction,),
            comment="Deep epistemic conflict or cognitive dissonance — more intense than PeerArgumentation.")
        C.TaskCoordination = make_class(onto, "TaskCoordination", bases=(C.CollaborativeDiscourseAction,),
            comment="Task allocation or division of labor discourse (e.g. 'You do X, I'll do Y').")
        C.PeerAssessment = make_class(onto, "PeerAssessment", bases=(C.CollaborativeDiscourseAction,),
            comment="Student evaluates or gives feedback on a peer's work.")

        # --- v2.1 NEW: S2D Bridge enhancement ---
        C.DesignJustification = make_class(onto, "DesignJustification", bases=(C.DesignReasoningAction,),
            comment="Student explicitly justifies a design decision based on scientific evidence or principles "
                    "(e.g. 'Based on our test, we set the blade angle at 30° for maximum efficiency'). "
                    "Key to completing the Science-to-Design evidence chain.")

        # v3.0: ConstraintReasoningAction — captures constraint-driven design adjustment
        C.ConstraintReasoningAction = make_class(onto, "ConstraintReasoningAction", bases=(C.DesignReasoningAction,),
            comment="Student reasons about design constraints and adjusts approach accordingly "
                    "(e.g. 'Limestone filter costs $120, over our $100 budget — we need an alternative'). "
                    "Key to modeling constraint-driven backtracking and trade-off analysis in real PBL.@en")

        intermediate_categories = [
            C.ScientificInquiryAction, C.DesignReasoningAction,
            C.CollaborativeDiscourseAction, C.HelpSeekingAction,
            C.SocialAffectiveAction, C.RegulatoryAction]
        declare_disjoint(*intermediate_categories)
        declare_covering(C.DiscourseAction, intermediate_categories)
        sci = [C.HypothesisProposing, C.EvidenceAnalyzing, C.PrincipleFormulating]
        declare_disjoint(*sci); declare_covering(C.ScientificInquiryAction, sci)
        des = [C.IdeaGeneration, C.PlanningUtterance, C.DesignJustification, C.ConstraintReasoningAction]
        declare_disjoint(*des); declare_covering(C.DesignReasoningAction, des)
        col = [C.PeerArgumentation, C.PeerTutoring, C.PeerAssessment, C.TaskCoordination, C.KnowledgeSharing, C.CognitiveConflict]
        declare_disjoint(*col); declare_covering(C.CollaborativeDiscourseAction, col)
        hlp = [C.HelpSeeking, C.ProcessConfusion, C.ClarificationQuestioning, C.FailureReporting]
        declare_disjoint(*hlp); declare_covering(C.HelpSeekingAction, hlp)
        soc = [C.SocialBonding, C.Agreement, C.Disagreement, C.PeerEncouragement, C.EmotiveExpression]
        declare_disjoint(*soc); declare_covering(C.SocialAffectiveAction, soc)
        reg = [C.Summarizing, C.TaskManagement, C.Demonstration, C.SerendipitousDiscovery,
               C.ReflectiveExpression]
        declare_disjoint(*reg); declare_covering(C.RegulatoryAction, reg)

        # Top-level disjointness
        declare_disjoint(C.Iteration, C.Reflection,
                         C.ReflectionLevel, C.IterationOutcome, C.DiscourseAction)

        # ── Object Properties ──


        C.hasSubIteration, C.isSubIterationOf = make_property_pair(onto,
            "hasSubIteration", "isSubIterationOf", C.Iteration, C.Iteration)
        C.hasSubIteration.comment.append(
            "Nested iteration: a micro-cycle inside a larger iteration (e.g. build→test→fix within a design iteration).@en")

        C.hasReflection, C.isReflectionOf = make_property_pair(onto,
            "hasReflection", "isReflectionOf",
            Or([C.Phase, C.Activity]), C.Reflection)

        C.hasReflectionLevel, C.isLevelOfReflection = make_property_pair(onto,
            "hasReflectionLevel", "isLevelOfReflection", C.Reflection, C.ReflectionLevel)

        # v4.1: event→product bridge. Any observable learning event (verbal,
        # written, or digital) may express a Reflection product. Attribution
        # (isAttributedTo) and timing (timestamp) live on the event, keeping
        # the product time-invariant while M5 evidence chains stay anchored.
        C.expressesReflection, C.isExpressedInLearningEvent = make_property_pair(onto,
            "expressesReflection", "isExpressedInLearningEvent",
            C.LearningEvent, C.Reflection)
        C.expressesReflection.comment.append(
            "Links an observable learning event (e.g. ReflectiveExpression, "
            "WrittenExpression) to the Reflection product it expresses. "
            "Bridges the event layer to the reflection product: attribution "
            "and timing live on the event; the product carries the text and "
            "its Kember level.@en")

        # Cross-module: LearningEvent → Phase (M1)
        # v3.1: domain broadened from DiscourseAction to LearningEvent so that
        # InstructorIntervention (M4) can also anchor to phases.
        C.occursInPhase, C.containsDiscourse = make_property_pair(onto,
            "occursInPhase", "containsDiscourse", C.LearningEvent, C.Phase)
        # v3.1: sub-phase anchoring (DiscourseAction → SubPhase). Grade-band
        # sub-phase decomposition stays transparent to the macro-phase rules,
        # while M5 evidence chains inherit sub-phase context via
        # PerformanceTrace —derivedFromEvent→ DiscourseAction —occursInSubPhase→ SubPhase.
        C.occursInSubPhase, C.containsSubPhaseAction = make_property_pair(onto,
            "occursInSubPhase", "containsSubPhaseAction", C.DiscourseAction, C.SubPhase)

        # Transitive discourse threading
        C.isFollowedByAction, C.isPrecededByAction = make_property_pair(onto,
            "isFollowedByAction", "isPrecededByAction",
            C.DiscourseAction, C.DiscourseAction, transitive=True)
        C.isFollowedByAction.comment.append("Generic transitive discourse thread.@en")

        # Sub-property: causal discourse link
        C.isTriggeredBy, C.triggersAction = make_property_pair(onto,
            "isTriggeredBy", "triggersAction", C.DiscourseAction, C.DiscourseAction)
        C.isTriggeredBy.comment.append("Causal discourse link.@en")

        # Iteration triggers
        C.iterationTriggeredBy, C.triggersIteration = make_property_pair(onto,
            "iterationTriggeredBy", "triggersIteration",
            C.Iteration, Or([C.Activity, C.DiscourseAction]))

        C.hasIterationOutcome, C.isOutcomeOfIteration = make_property_pair(onto,
            "hasIterationOutcome", "isOutcomeOfIteration", C.Iteration, C.IterationOutcome)

        # Cross-module: DiscourseAction → Concept (M2)
        C.referencesConcept, C.isReferencedByAction = make_property_pair(onto,
            "referencesConcept", "isReferencedByAction", C.DiscourseAction, C.Concept)

        # S2D Bridge: informsDesign (Science-to-Design cognitive link)
        C.informsDesign, C.isInformedByScience = make_property_pair(onto,
            "informsDesign", "isInformedByScience",
            C.DiscourseAction, Or([C.DesignActivity, C.MakingActivity]))
        C.informsDesign.comment.append(
            "S2D Bridge: A scientific discourse action directly informs a "
            "subsequent engineering activity. Hard computational evidence of "
            "the Science-to-Design cognitive trajectory (Informed Design).@en")

        # D2S Bridge: motivatesInquiry (Design-to-Science cognitive link)
        C.motivatesInquiry, C.isMotivatedBy = make_property_pair(onto,
            "motivatesInquiry", "isMotivatedBy",
            Or([C.FailureReporting, C.IterationOutcome]),
            Or([C.HypothesisProposing, C.InquiryActivity]))
        C.motivatesInquiry.comment.append(
            "D2S Bridge: A failure report or iteration outcome motivates "
            "scientific inquiry (hypothesis proposing or investigation). "
            "Captures the Design-to-Science cognitive pathway — the moment "
            "an engineering prototype fails, prompting students to ask "
            "scientific questions and conduct research. Complements the "
            "S2D informsDesign bridge for full bidirectional cognitive tracing.@en")

        # S2D Bridge v2.1: DesignJustification links evidence/principles to design decisions
        C.justifiesDecision, C.isDecisionJustifiedBy = make_property_pair(onto,
            "justifiesDecision", "isDecisionJustifiedBy",
            C.DiscourseAction, C.DesignJustification)
        C.justifiesDecision.comment.append(
            "A design justification is supported by a scientific discourse action "
            "(Hypothesis, Evidence, or Principle). Completes the S2D evidence chain.@en")

        # Placeholder: isAttributedTo — refined by M4
        C.isAttributedTo, C.performsAction = make_property_pair(onto,
            "isAttributedTo", "performsAction", C.LearningEvent, Thing)

        # Iteration-EDP tracking


        # ── Data Properties ──
        C.timestamp = make_datatype_prop(onto, "timestamp", [C.LearningEvent], dt.datetime)
        C.utteranceText = make_datatype_prop(onto, "utteranceText", [C.DiscourseAction], str)
        C.utteranceText.comment.append("The textual content of a discourse action.@en")
        C.iterationNumber = make_datatype_prop(onto, "iterationNumber", [C.Iteration], int)
        C.reflectionText = make_datatype_prop(onto, "reflectionText", [C.Reflection], str)
        C.reflectionText.comment.append("The textual content of a reflection.@en")
        C.estimatedDuration = make_datatype_prop(onto, "estimatedDuration", [C.Activity], int)
        C.estimatedDuration.comment.append("Estimated duration of an activity in minutes.@en")
        C.valence = make_datatype_prop(onto, "valence", [C.EmotiveExpression], str)
        C.valence.comment.append("Emotional valence of an EmotiveExpression (e.g. positive, negative, neutral).@en")

        # ── Learning Event (abstract base for all observable behaviors) ──
        # v3.1: moved back to M3, its conceptual home (the event layer).
        # v3.0 had placed it in Core to resolve an M3↔M4 import cycle; that
        # cycle no longer exists (M4 already references M3 classes, and
        # isAttributedTo uses the placeholder-range + M5 refinement pattern).
        # DiscourseAction, NonverbalAction (M3), and InstructorIntervention (M4)
        # all extend this class; extension point for future event types
        # (e.g. AILearningEvent).


        # Nonverbal actions (parallel to DiscourseAction, both ⊑ LearningEvent)
        C.DiscourseAction.is_a.append(C.LearningEvent)
        C.NonverbalAction = make_class(onto, "NonverbalAction", bases=(C.LearningEvent,),
            comment="Non-verbal learning behavior: physical prototyping, tool sharing, gazing, etc.")
        C.PhysicalPrototyping = make_class(onto, "PhysicalPrototyping", bases=(C.NonverbalAction,),
            comment="Student engages in hands-on building or assembly.")
        C.ToolSharing = make_class(onto, "ToolSharing", bases=(C.NonverbalAction,),
            comment="Student shares tools or materials with a peer.")
        C.GazingAtPeerWork = make_class(onto, "GazingAtPeerWork", bases=(C.NonverbalAction,),
            comment="Student observes peer's work — may indicate learning or distraction.")
        C.IdleBehavior = make_class(onto, "IdleBehavior", bases=(C.NonverbalAction,),
            comment="Student is disengaged: staring blankly, playing with materials off-task.")
        C.CelebrationGesture = make_class(onto, "CelebrationGesture", bases=(C.NonverbalAction,),
            comment="Student expresses joy/success nonverbally: cheering, high-fiving, jumping up.")
        C.MaterialHoarding = make_class(onto, "MaterialHoarding", bases=(C.NonverbalAction,),
            comment="Student monopolizes materials — negative collaboration signal.")
        # v2.1: Additional NonverbalAction types
        C.Gesturing = make_class(onto, "Gesturing", bases=(C.NonverbalAction,),
            comment="Student uses hand gestures to indicate, describe, or emphasize (e.g. pointing, measuring with hands).")
        C.Nodding = make_class(onto, "Nodding", bases=(C.NonverbalAction,),
            comment="Student nods in agreement or understanding — positive collaboration signal.")
        C.FacialExpression = make_class(onto, "FacialExpression", bases=(C.NonverbalAction,),
            comment="Student displays a facial expression indicating confusion, surprise, concentration, or frustration.")
        C.WrittenExpression = make_class(onto, "WrittenExpression", bases=(C.NonverbalAction,),
            comment="Student writes, draws, or sketches on paper/whiteboard — important nonverbal cognitive expression.")
        declare_disjoint(C.PhysicalPrototyping, C.ToolSharing, C.GazingAtPeerWork,
                         C.IdleBehavior, C.CelebrationGesture, C.MaterialHoarding,
                         C.Gesturing, C.Nodding, C.FacialExpression, C.WrittenExpression)
        declare_covering(C.NonverbalAction, [C.PhysicalPrototyping, C.ToolSharing,
                         C.GazingAtPeerWork, C.IdleBehavior,
                         C.CelebrationGesture, C.MaterialHoarding,
                         C.Gesturing, C.Nodding, C.FacialExpression, C.WrittenExpression])

        # v3.0: urgency and triggerConfidence moved from M5 (Anchor) to M3 (Process)
        # because their domain is DiscourseAction (M3). Keeps property with its domain class.
        C.urgency = make_datatype_prop(onto, "urgency", [C.DiscourseAction], float)
        C.urgency.comment.append(
            "Urgency/priority level (0-1) for agent response arbitration. "
            "When multiple SWRL rules fire simultaneously, higher urgency triggers first.@en")
        C.triggerConfidence = make_datatype_prop(onto, "triggerConfidence", [C.DiscourseAction], float)
        C.triggerConfidence.comment.append(
            "SWRL reasoning confidence score (0-1) for this trigger. "
            "Enables threshold-based filtering of low-confidence agent activations.@en")

        # ── v3.0: Cross-team interaction properties ──
        # Enables modeling of gallery walks, cross-team peer review,
        # instructor cross-team comparisons, and inter-team ideation transfer.
        C.directedToTeam, C.isTargetedByAction = make_property_pair(onto,
            "directedToTeam", "isTargetedByAction", C.DiscourseAction, Thing)  # range tightened to Team in M4
        C.directedToTeam.comment.append(
            "A discourse action directed at another team (e.g. gallery walk feedback, "
            "cross-team peer review). Distinguishes intra-team from inter-team discourse.@en")
        C.referencesTeamWork, C.isReferencedByTeam = make_property_pair(onto,
            "referencesTeamWork", "isReferencedByTeam", C.DiscourseAction, Thing)  # range tightened to Team in M4
        C.referencesTeamWork.comment.append(
            "A discourse action that references another team's work product or process. "
            "Captures cross-team ideation transfer and comparative reasoning.@en")
        C.isAddressedToClass = make_datatype_prop(onto, "isAddressedToClass", [C.DiscourseAction], bool)
        C.isAddressedToClass.comment.append(
            "Whether this discourse action is addressed to the whole class "
            "(e.g. during final presentations, gallery walk debriefs).@en")

        # v3.0: Tighten expressesPerspective domain (defined in M2 with placeholder domain)
        C.expressesPerspective.domain = [C.DiscourseAction]
        C.isExpressedInAction.range = [C.DiscourseAction]

    print(f"  ✓ M3 Process: {_count(onto, 'classes')} classes, {_count(onto, 'object_properties')} obj props, {_count(onto, 'data_properties')} data props")
    return onto


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE 4: HYBRID TEAM
# ═══════════════════════════════════════════════════════════════════════════════

def build_team():
    """Build Module 4: HybridTeam — Actors, Teams, Roles."""
    onto = get_ontology(MODULE_IRIS["team"])

    with onto:
        # ── Actor Hierarchy ──
        C.Actor = make_class(onto, "Actor",
            comment="Abstract top class for all participants (human and AI) in a PBL team.")
        C.HumanActor = make_class(onto, "HumanActor", bases=(C.Actor,),
            comment="A human participant in a PBL team.")
        C.Learner = make_class(onto, "Learner", bases=(C.HumanActor,),
            comment="A student participating in the PBL project.")
        C.Instructor = make_class(onto, "Instructor", bases=(C.HumanActor,),
            comment="A teacher or facilitator guiding the PBL process.")
        C.VirtualAgent = make_class(onto, "VirtualAgent", bases=(C.Actor,),
            comment="An AI pedagogical agent endowed with a specific scaffolding role.")

        C.ProceduralGuide = make_class(onto, "ProceduralGuide", bases=(C.VirtualAgent,),
            comment="Scaffolds procedural steps in the engineering design process (Hannafin: Procedural).")
        C.ConceptualExpert = make_class(onto, "ConceptualExpert", bases=(C.VirtualAgent,),
            comment="Provides domain-specific knowledge and conceptual explanations (Hannafin: Conceptual).")
        C.MetacognitiveChallenger = make_class(onto, "MetacognitiveChallenger", bases=(C.VirtualAgent,),
            comment="Prompts reflection, self-monitoring, and self-regulation (Hannafin: Metacognitive).")
        C.DivergentBrainstormer = make_class(onto, "DivergentBrainstormer", bases=(C.VirtualAgent,),
            comment="Stimulates creative ideation and alternative perspectives (Hannafin: Strategic/Divergent).")
        C.SafetyMonitor = make_class(onto, "SafetyMonitor", bases=(C.VirtualAgent,),
            comment="Monitors physical and digital safety risks in PBL activities, especially during prototyping and testing.")
        # v4.0: AffectiveSupporter — the sixth archetype, grounded in social-emotional
        # learning (SEL) and psychological-safety scaffolding. Fills the gap exposed
        # by expert validity (Experiment B): affective support is a distinct
        # scaffolding dimension absent from Hannafin's four plus safety.
        C.AffectiveSupporter = make_class(onto, "AffectiveSupporter", bases=(C.VirtualAgent,),
            comment="Provides affective and motivational support: empathy, encouragement, "
                    "emotion regulation, and psychological-safety maintenance (SEL / affective scaffolding).")

        declare_covering(C.Actor, [C.HumanActor, C.VirtualAgent])
        declare_covering(C.HumanActor, [C.Learner, C.Instructor])
        declare_covering(C.VirtualAgent,
            [C.ProceduralGuide, C.ConceptualExpert, C.MetacognitiveChallenger, C.DivergentBrainstormer, C.SafetyMonitor, C.AffectiveSupporter])
        declare_disjoint(C.HumanActor, C.VirtualAgent)
        declare_disjoint(C.Learner, C.Instructor)
        declare_disjoint(C.ProceduralGuide, C.ConceptualExpert,
                         C.MetacognitiveChallenger, C.DivergentBrainstormer, C.SafetyMonitor, C.AffectiveSupporter)

        # ── Team ──
        C.Team = make_class(onto, "Team",
            comment="A collaborative group of human learners working on a PBL project. CSCL fundamental unit.")

        # ── Human Roles (Division of Labor) ──
        C.HumanRole = make_class(onto, "HumanRole",
            comment="A functional role within a PBL team. Disjoint from Actor hierarchy.")
        C.Programmer = make_class(onto, "Programmer", bases=(C.HumanRole,))
        C.Builder = make_class(onto, "Builder", bases=(C.HumanRole,))
        C.ProjectManager = make_class(onto, "ProjectManager", bases=(C.HumanRole,))
        # v2.1: Extended roles for broader K-12 PBL coverage
        C.Researcher = make_class(onto, "Researcher", bases=(C.HumanRole,),
            comment="Student responsible for research, data collection, and evidence gathering.")
        C.Designer = make_class(onto, "Designer", bases=(C.HumanRole,),
            comment="Student responsible for sketching, CAD, and design visualization.")
        C.Presenter = make_class(onto, "Presenter", bases=(C.HumanRole,),
            comment="Student responsible for final presentations and public communication.")
        C.MaterialManager = make_class(onto, "MaterialManager", bases=(C.HumanRole,),
            comment="Student responsible for managing materials, tools, and workspace organization.")
        declare_disjoint(C.Programmer, C.Builder, C.ProjectManager,
                         C.Researcher, C.Designer, C.Presenter, C.MaterialManager)
        declare_disjoint(C.Actor, C.HumanRole)
        declare_disjoint(C.Team, C.Actor, C.HumanRole)

        # ── Object Properties ──
        C.hasTeam, C.isTeamOf = make_property_pair(onto,
            "hasTeam", "isTeamOf", C.Project, C.Team)

        C.hasTeamMember, C.isMemberOf = make_property_pair(onto,
            "hasTeamMember", "isMemberOf", C.Team, C.HumanActor)

        C.interactsWith = type("interactsWith", (SymmetricProperty, ObjectProperty), {"namespace": onto})
        C.interactsWith.label.append("interacts with@en")
        C.interactsWith.comment.append("Symmetric interaction relation between Actors.@en")
        C.interactsWith.domain.append(C.Actor)
        C.interactsWith.range.append(C.Actor)

        C.monitorsTeam, C.isMonitoredByAgent = make_property_pair(onto,
            "monitorsTeam", "isMonitoredByAgent", C.VirtualAgent, C.Team)
        C.monitorsTeam.comment.append(
            "A VirtualAgent monitors the group discourse of a Team. Agents operate at the group level, not individual.@en")

        C.playsRole, C.isPlayedBy = make_property_pair(onto,
            "playsRole", "isPlayedBy", C.Learner, C.HumanRole)

        # Instructor Intervention (from teacher review)
        C.InstructorIntervention = make_class(onto, "InstructorIntervention", bases=(C.LearningEvent,),
            comment="A deliberate instructional intervention by the teacher during PBL.")
        C.SafetyIntervention = make_class(onto, "SafetyIntervention", bases=(C.InstructorIntervention,),
            comment="Instructor intervenes to address a physical or digital safety concern.")
        C.DirectionalGuidance = make_class(onto, "DirectionalGuidance", bases=(C.InstructorIntervention,),
            comment="Instructor provides procedural or strategic direction to advance the project.")
        C.DeepQuestioning = make_class(onto, "DeepQuestioning", bases=(C.InstructorIntervention,),
            comment="Instructor uses Socratic or probing questions to deepen student thinking.")
        C.EmotionalSupport = make_class(onto, "EmotionalSupport", bases=(C.InstructorIntervention,),
            comment="Instructor provides emotional or motivational support to students.")
        C.ClassroomManagement = make_class(onto, "ClassroomManagement", bases=(C.InstructorIntervention,),
            comment="Instructor manages classroom logistics, transitions, or behavior.")
        C.TimeManagement = make_class(onto, "TimeManagement", bases=(C.InstructorIntervention,),
            comment="Instructor intervenes to keep the project on schedule or adjust pacing.")

        declare_disjoint(C.SafetyIntervention, C.DirectionalGuidance, C.DeepQuestioning,
                         C.EmotionalSupport, C.ClassroomManagement, C.TimeManagement)
        declare_covering(C.InstructorIntervention,
            [C.SafetyIntervention, C.DirectionalGuidance, C.DeepQuestioning,
             C.EmotionalSupport, C.ClassroomManagement, C.TimeManagement])

        C.overridesAgent, C.isOverriddenByInstructor = make_property_pair(onto,
            "overridesAgent", "isOverriddenByInstructor", C.InstructorIntervention, C.VirtualAgent)
        C.overridesAgent.comment.append(
            "An instructor can override or supplement a VirtualAgent's recommendation.@en")

        # v2.1: Instructor-Team relationship (separate from Team membership)
        C.instructsTeam, C.isInstructedBy = make_property_pair(onto,
            "instructsTeam", "isInstructedBy", C.Instructor, C.Team)
        C.instructsTeam.comment.append(
            "An instructor provides guidance to a team. Distinguished from isMemberOf "
            "because instructors are not 'team members' but cross-team facilitators.@en")

        # v2.1: Directional interaction sub-properties of interactsWith
        C.speaksTo, C.isSpokenToBy = make_property_pair(onto,
            "speaksTo", "isSpokenToBy", C.Actor, C.Actor)
        C.speaksTo.comment.append("Directional verbal interaction: one actor speaks to another.@en")
        C.respondsTo, C.isRespondedToBy = make_property_pair(onto,
            "respondsTo", "isRespondedToBy", C.Actor, C.Actor)
        C.respondsTo.comment.append("Directional response: one actor replies to another.@en")
        C.sharesWith, C.isSharedWithBy = make_property_pair(onto,
            "sharesWith", "isSharedWithBy", C.Actor, C.Actor)
        C.sharesWith.comment.append("Directional sharing: one actor shares resources or information with another.@en")

        # KG-driven guardrail: VirtualAgent → DomainBoundary (M2)
        C.hasDomainBoundary, C.isDomainOfAgent = make_property_pair(onto,
            "hasDomainBoundary", "isDomainOfAgent", C.VirtualAgent, C.DomainBoundary)
        C.hasDomainBoundary.comment.append(
            "KG-driven guardrail: defines the epistemological scope within which a VirtualAgent can operate.@en")
        C.ConceptualExpert.is_a.append(C.hasDomainBoundary.some(C.DomainBoundary))

        # Bridge M3→M4: Actor → LearningEvent
        # v3.0: isAttributedTo refinement (range=Actor, inverse=hasDiscourseAction)
        # moved to M5 (Anchor) — resolves M3↔M4 circular dependency
        C.hasDiscourseAction = type("hasDiscourseAction", (ObjectProperty,), {"namespace": onto})
        C.hasDiscourseAction.label.append("has discourse action@en")
        C.hasDiscourseAction.comment.append(
            "An Actor produces a learning event (discourse or nonverbal). "
            "Completes the M3:M4 bridge. Range matches isAttributedTo's domain "
            "(LearningEvent) so nonverbal and instructor events are not entailed "
            "as DiscourseActions.@en")
        C.hasDiscourseAction.domain.append(C.Actor)
        C.hasDiscourseAction.range.append(C.LearningEvent)

        # Forward reference to M5 (will be tightened in build_anchor)
        C.hasCompetency = type("hasCompetency", (ObjectProperty,), {"namespace": onto})
        C.hasCompetency.label.append("has competency@en")
        C.hasCompetency.comment.append("Forward reference to Module 5. A Learner possesses a measurable CompetencyDimension.@en")
        C.hasCompetency.domain.append(C.Learner)
        C.hasCompetency.range.append(Thing)

        # ── Data Properties ──
        C.personaPrompt = make_datatype_prop(onto, "personaPrompt", [C.VirtualAgent], str)
        C.hasName = make_datatype_prop(onto, "hasName", [C.HumanActor], str)
        # v2.1: Structured scaffolding parameters
        C.responseTemplate = make_datatype_prop(onto, "responseTemplate", [C.VirtualAgent], str)
        C.responseTemplate.comment.append(
            "Structured response format template for LLM output (e.g. '{\"message\": ..., \"scaffold_level\": ...}').@en")
        # v3.0: responseFormat moved from M5 (Anchor) to M4 (Team)
        # because its domain is VirtualAgent (M4)
        C.responseFormat = make_datatype_prop(onto, "responseFormat", [C.VirtualAgent], str)
        C.responseFormat.comment.append(
            "Expected response format for the agent: 'text', 'json', 'markdown', 'socratic'.@en")
        C.interventionThreshold = make_datatype_prop(onto, "interventionThreshold", [C.VirtualAgent], float)
        C.interventionThreshold.comment.append(
            "Confidence/urgency threshold (0-1) for the agent to intervene. Higher = less intrusive.@en")
        C.scaffoldingFadeRate = make_datatype_prop(onto, "scaffoldingFadeRate", [C.VirtualAgent], float)
        C.scaffoldingFadeRate.comment.append(
            "Rate (0-1) at which scaffolding is withdrawn as learner competence increases (Hannafin: fading).@en")
        # v2.1: ZPD (Vygotsky, 1978) for learner development tracking
        C.hasZPDCurrentLevel = make_datatype_prop(onto, "hasZPDCurrentLevel", [C.Learner], str)
        C.hasZPDCurrentLevel.comment.append(
            "The learner's current independent performance level (ZPD actual development level). "
            "Value references a CompetencyDimension name or proficiency label.@en")
        C.hasZPDPotentialLevel = make_datatype_prop(onto, "hasZPDPotentialLevel", [C.Learner], str)
        C.hasZPDPotentialLevel.comment.append(
            "The learner's potential performance level with scaffolding (ZPD proximal development). "
            "The gap between current and potential defines the ZPD.@en")

        # v3.0: Per-student phase tracking — supports multi-agent orchestration
        # and assessment at the individual learner level. Each learner can be in
        # a different phase simultaneously (e.g. Alice in ScientificInvestigation
        # while Bob is in Implementation).
        C.learnerCurrentPhase = type("learnerCurrentPhase", (ObjectProperty,), {"namespace": onto})
        C.learnerCurrentPhase.label.append("learner current phase@en")
        C.learnerCurrentPhase.comment.append(
            "The phase a specific learner is currently engaged in. Enables per-learner "
            "phase tracking for multi-agent orchestration and individualized assessment. "
            "Distinct from Project.hasPhase which defines the official timeline.@en")
        C.learnerCurrentPhase.domain.append(C.Learner)
        C.learnerCurrentPhase.range.append(C.Phase)

        # v3.0: Tighten cross-module property ranges defined elsewhere
        C.isProducedBy.range = [C.Learner]
        C.producesDeliverable.domain = [C.Learner]
        C.directedToTeam.range = [C.Team]
        C.isTargetedByAction.domain = [C.Team]
        C.referencesTeamWork.range = [C.Team]
        C.isReferencedByTeam.domain = [C.Team]

    print(f"  ✓ M4 Team: {_count(onto, 'classes')} classes, {_count(onto, 'object_properties')} obj props, {_count(onto, 'data_properties')} data props")
    return onto


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE 5: SEMANTIC ANCHOR
# ═══════════════════════════════════════════════════════════════════════════════

def build_anchor():
    """Build Module 5: SemanticAnchor — Multi-purpose bridge module.

    v3.0: Organized into 4 bridge areas, each an independent extension point.
    New bridges (e.g. ResourceBridge, EmotionBridge) follow the same pattern
    without modifying other modules.

    Bridge Areas:
      A. Orchestration Bridge  — DiscourseAction → VirtualAgent triggering
      B. Assessment Bridge     — Competency tracing and evidence chains
      C. Analytics Bridge      — Teacher dashboard and team state monitoring
      D. Standards Bridge      — Curriculum standard alignment
    """
    onto = get_ontology(MODULE_IRIS["anchor"])

    with onto:
        # ═════════════════════════════════════════════════════════════════
        # BRIDGE AREA A — Orchestration Bridge
        # Links M3 (LearningEvent) → M4 (VirtualAgent) for SWRL-driven
        # agent triggering. Extension: add trigger sub-properties for
        # finer-grained control.
        # ═════════════════════════════════════════════════════════════════
        C.triggersAgent, C.isTriggeredByDiscourse = make_property_pair(onto,
            "triggersAgent", "isTriggeredByDiscourse", C.LearningEvent, C.VirtualAgent)
        C.triggersAgent.comment.append(
            "Maps a LearningEvent (DiscourseAction, NonverbalAction, or InstructorIntervention) "
            "to the VirtualAgent that should respond. Trigger conditions encoded in SWRL rules. "
            "Cross-module: M3 → M4.@en")

        # v4.0: actor attribution for reified boundary-crossing events (M2).
        # M2 defines the event; M5 (Anchor) wires it to the M4 Actor hierarchy,
        # mirroring the isAttributedTo dependency-inversion pattern.
        C.hasCrossingActor, C.isCrossingActorOf = make_property_pair(onto,
            "hasCrossingActor", "isCrossingActorOf", C.BoundaryCrossingEvent, C.Actor)

        # v3.0: isAttributedTo refinement moved from M4 to M5.
        # M3 defines isAttributedTo with range=Thing as a placeholder;
        # M5 tightens it to Actor and links it to hasDiscourseAction.
        # This keeps M3 free of M4 references (resolves circular dependency).
        C.isAttributedTo.range = [C.Actor]
        C.performsAction.domain = [C.Actor]
        C.performsAction.range = [C.LearningEvent]
        C.isAttributedTo.inverse_property = C.hasDiscourseAction

        # ═════════════════════════════════════════════════════════════════
        # BRIDGE AREA B — Assessment Bridge
        # Competency dimensions, performance traces, cognitive steps.
        # Implements Evidence-Centered Design (ECD, Mislevy et al. 2003)
        # with three-hop traceability:
        #   DiscourseAction → hasCognitiveStep → CognitiveStep
        #   → evidencesCompetency → CompetencyDimension
        # ═════════════════════════════════════════════════════════════════
        C.CompetencyDimension = make_class(onto, "CompetencyDimension",
            comment="A measurable competency dimension for process-oriented assessment.")
        C.EngineeringThinking = make_class(onto, "EngineeringThinking", bases=(C.CompetencyDimension,),
            comment="Ability to apply engineering design process, constraint analysis, and systematic problem-solving.")
        C.CollaborativeTeamwork = make_class(onto, "CollaborativeTeamwork", bases=(C.CompetencyDimension,),
            comment="Ability to collaborate, communicate, and coordinate within a team (CSCL).")
        C.InterdisciplinaryIntegration = make_class(onto, "InterdisciplinaryIntegration", bases=(C.CompetencyDimension,),
            comment="Ability to integrate concepts and methods across disciplinary boundaries (Klein).")
        C.CreativityAndInnovation = make_class(onto, "CreativityAndInnovation", bases=(C.CompetencyDimension,),
            comment="Ability to generate novel ideas, discover unexpected connections, and innovate within design constraints.")
        C.MetacognitiveSelfRegulation = make_class(onto, "MetacognitiveSelfRegulation", bases=(C.CompetencyDimension,),
            comment="Ability to reflect on one's own learning process, monitor understanding, and self-regulate cognitive strategies.")

        # Level-2 sub-dimensions (for granular assessment)
        C.ProblemDecomposition = make_class(onto, "ProblemDecomposition", bases=(C.EngineeringThinking,),
            comment="Ability to break down complex problems into manageable sub-problems.")
        C.ConstraintAnalysis = make_class(onto, "ConstraintAnalysis", bases=(C.EngineeringThinking,),
            comment="Ability to identify, analyze, and work within design constraints.")
        C.SystematicTesting = make_class(onto, "SystematicTesting", bases=(C.EngineeringThinking,),
            comment="Ability to design and execute tests to evaluate a solution.")
        C.FailureAnalysis = make_class(onto, "FailureAnalysis", bases=(C.EngineeringThinking,),
            comment="Ability to analyze failures and extract actionable insights (Productive Failure).")
        C.IterativeImprovement = make_class(onto, "IterativeImprovement", bases=(C.EngineeringThinking,),
            comment="Ability to iteratively refine a design based on feedback and test results.")

        C.CommunicationSkill = make_class(onto, "CommunicationSkill", bases=(C.CollaborativeTeamwork,),
            comment="Ability to articulate ideas clearly to team members.")
        C.ConflictResolution = make_class(onto, "ConflictResolution", bases=(C.CollaborativeTeamwork,),
            comment="Ability to navigate and resolve disagreements constructively.")
        C.RoleResponsibility = make_class(onto, "RoleResponsibility", bases=(C.CollaborativeTeamwork,),
            comment="Ability to fulfill assigned team role with accountability.")

        # InterdisciplinaryIntegration sub-dimensions
        C.CrossDomainConceptRecognition = make_class(onto, "CrossDomainConceptRecognition", bases=(C.InterdisciplinaryIntegration,),
            comment="Ability to recognize and identify concepts spanning multiple disciplinary domains.")
        C.AnalogicalTransfer = make_class(onto, "AnalogicalTransfer", bases=(C.InterdisciplinaryIntegration,),
            comment="Ability to transfer principles and patterns analogically from one domain to another.")
        C.IntegratedExplanation = make_class(onto, "IntegratedExplanation", bases=(C.InterdisciplinaryIntegration,),
            comment="Ability to synthesize and articulate explanations that integrate multiple disciplinary perspectives.")
        declare_disjoint(C.CrossDomainConceptRecognition, C.AnalogicalTransfer, C.IntegratedExplanation)
        declare_covering(C.InterdisciplinaryIntegration,
            [C.CrossDomainConceptRecognition, C.AnalogicalTransfer, C.IntegratedExplanation])

        declare_disjoint(C.EngineeringThinking, C.CollaborativeTeamwork, C.InterdisciplinaryIntegration,
                         C.CreativityAndInnovation, C.MetacognitiveSelfRegulation)
        declare_covering(C.CompetencyDimension,
            [C.EngineeringThinking, C.CollaborativeTeamwork, C.InterdisciplinaryIntegration,
             C.CreativityAndInnovation, C.MetacognitiveSelfRegulation])

        C.PerformanceTrace = make_class(onto, "PerformanceTrace",
            comment="A timestamped record of a learner's performance on a specific competency, anchored to a PBL event.")
        C.CompetencyProfile = make_class(onto, "CompetencyProfile",
            comment="An aggregated competency profile for a learner, collecting multiple PerformanceTraces over time.")
        declare_disjoint(C.CompetencyDimension, C.PerformanceTrace, C.CompetencyProfile)

        # Assessment properties
        C.tracesCompetency, C.isTracedByPerformance = make_property_pair(onto,
            "tracesCompetency", "isTracedByPerformance", C.PerformanceTrace, C.CompetencyDimension)

        # v2.1: CognitiveStep for explainable traceability between discourse and competency
        C.CognitiveStep = make_class(onto, "CognitiveStep",
            comment="A cognitive operation that bridges discourse actions to competency evidence. "
                    "Enables explainable three-hop traceability: "
                    "DiscourseAction → hasCognitiveStep → CognitiveStep → evidencesCompetency → CompetencyDimension.@en")
        C.hasCognitiveStep, C.isCognitiveStepOf = make_property_pair(onto,
            "hasCognitiveStep", "isCognitiveStepOf", C.DiscourseAction, C.CognitiveStep)
        C.evidencesCompetency, C.isEvidencedBy = make_property_pair(onto,
            "evidencesCompetency", "isEvidencedBy", C.CognitiveStep, C.CompetencyDimension)
        C.stepType = make_datatype_prop(onto, "stepType", [C.CognitiveStep], str)
        C.stepType.comment.append(
            "Type label for the cognitive step: 'analogical_reasoning', 'causal_attribution', "
            "'hypothesis_testing', 'abstraction', 'problem_decomposition'.@en")
        declare_disjoint(C.CognitiveStep, C.CompetencyDimension, C.PerformanceTrace, C.CompetencyProfile)

        C.hasPerformanceTrace, C.isGeneratedByLearner = make_property_pair(onto,
            "hasPerformanceTrace", "isGeneratedByLearner", C.Learner, C.PerformanceTrace)

        C.hasCompetencyProfile, C.isProfileOf = make_property_pair(onto,
            "hasCompetencyProfile", "isProfileOf", C.Learner, C.CompetencyProfile)

        C.aggregatesTrace, C.isAggregatedIn = make_property_pair(onto,
            "aggregatesTrace", "isAggregatedIn", C.CompetencyProfile, C.PerformanceTrace)

        # Data lineage: PerformanceTrace → originating PBL event
        C.derivedFromEvent, C.generatesTrace = make_property_pair(onto,
            "derivedFromEvent", "generatesTrace",
            C.PerformanceTrace, Or([C.Activity, C.DiscourseAction, C.Reflection, C.ReflectionLevel]))
        C.derivedFromEvent.comment.append(
            "Anchors a PerformanceTrace to the PBL event it was derived from. "
            "Provides unbroken evidence chain for process-oriented assessment.@en")

        # ═════════════════════════════════════════════════════════════════
        # BRIDGE AREA C — Analytics Bridge (Teacher Dashboard)
        # Team state snapshots with configurable indicators and alert
        # thresholds. Extension: add new AnalyticsIndicator subclasses
        # without modifying other modules.
        # ═════════════════════════════════════════════════════════════════
        C.TeamState = make_class(onto, "TeamState",
            comment="A snapshot of team status at a specific point in time.")
        C.AnalyticsIndicator = make_class(onto, "AnalyticsIndicator",
            comment="Unified abstract class for all dashboard analytics indicators.")
        C.ProcessIndicator = make_class(onto, "ProcessIndicator", bases=(C.AnalyticsIndicator,))
        C.CollaborationIndicator = make_class(onto, "CollaborationIndicator", bases=(C.AnalyticsIndicator,))
        C.OutcomeIndicator = make_class(onto, "OutcomeIndicator", bases=(C.AnalyticsIndicator,))
        declare_disjoint(C.ProcessIndicator, C.CollaborationIndicator, C.OutcomeIndicator)
        declare_covering(C.AnalyticsIndicator,
            [C.ProcessIndicator, C.CollaborationIndicator, C.OutcomeIndicator])
        declare_disjoint(C.TeamState, C.AnalyticsIndicator)

        C.hasTeamState, C.isStateOfTeam = make_property_pair(onto,
            "hasTeamState", "isStateOfTeam", C.Team, C.TeamState)

        C.hasAnalyticsIndicator, C.isIndicatorOfState = make_property_pair(onto,
            "hasAnalyticsIndicator", "isIndicatorOfState", C.TeamState, C.AnalyticsIndicator)

        # ── Data Properties ──
        C.collaborationIndex = make_datatype_prop(onto, "collaborationIndex", [C.TeamState], float)
        C.collaborationIndex.comment.append("Overall CSCL collaboration quality index (0-1).@en")
        C.participationEquity = make_datatype_prop(onto, "participationEquity", [C.TeamState], float)
        C.participationEquity.comment.append("Gini-based equity of participation across team members.@en")
        C.transactivityIndex = make_datatype_prop(onto, "transactivityIndex", [C.TeamState], float)
        C.transactivityIndex.comment.append("Degree of cross-referencing and building on peer contributions.@en")
        C.knowledgeCoConstruction = make_datatype_prop(onto, "knowledgeCoConstruction", [C.TeamState], float)
        C.knowledgeCoConstruction.comment.append("Level of collaborative knowledge building (Scardamalia & Bereiter).@en")
        C.snapshotTime = make_datatype_prop(onto, "snapshotTime", [C.TeamState], dt.datetime)
        C.snapshotTime.comment.append(
            "Timestamp of the team state snapshot. Enables time-series trend analysis "
            "and dashboard visualizations of team dynamics over time.@en")
        C.indicatorValue = make_datatype_prop(onto, "indicatorValue", [C.AnalyticsIndicator], float)
        C.indicatorValue.comment.append("Quantitative value of an AnalyticsIndicator.@en")
        C.alertThresholdWarning = make_datatype_prop(onto, "alertThresholdWarning", [C.AnalyticsIndicator], float)
        C.alertThresholdWarning.comment.append(
            "Warning threshold: when indicatorValue falls below this, show yellow alert on dashboard.@en")
        C.alertThresholdCritical = make_datatype_prop(onto, "alertThresholdCritical", [C.AnalyticsIndicator], float)
        C.alertThresholdCritical.comment.append(
            "Critical threshold: when indicatorValue falls below this, show red alert on dashboard.@en")
        C.competencyScore = make_datatype_prop(onto, "competencyScore", [C.PerformanceTrace], float)
        C.recordedAt = make_datatype_prop(onto, "recordedAt", [C.PerformanceTrace], dt.datetime)
        # v2.1: Grade band and standard alignment
        C.hasGradeBand = make_datatype_prop(onto, "hasGradeBand", [C.CompetencyDimension], str)
        C.hasGradeBand.comment.append(
            "K-12 grade band for which this competency dimension applies: "
            "'K-2', '3-5', '6-8', '9-12'. Allows differentiation of expected proficiency by age group.@en")

        # ═════════════════════════════════════════════════════════════════
        # BRIDGE AREA D — Standards Bridge
        # Links CompetencyDimensions to external curriculum standards
        # (NGSS, CSTA, Common Core, ITEEA). Extension: add new frameworks
        # by creating StandardAlignment instances with new standardFramework values.
        # ═════════════════════════════════════════════════════════════════
        C.StandardAlignment = make_class(onto, "StandardAlignment",
            comment="Maps a CompetencyDimension to an external curriculum standard (NGSS, CSTA, Common Core, ITEEA).@en")
        C.hasAlignment, C.isAlignmentOf = make_property_pair(onto,
            "hasAlignment", "isAlignmentOf", C.CompetencyDimension, C.StandardAlignment)
        C.standardFramework = make_datatype_prop(onto, "standardFramework", [C.StandardAlignment], str)
        C.standardFramework.comment.append("Curriculum standard framework: 'NGSS', 'CSTA', 'CommonCore', 'ITEEA'.@en")
        C.standardCode = make_datatype_prop(onto, "standardCode", [C.StandardAlignment], str)
        C.standardCode.comment.append("Standard identifier code (e.g. 'NGSS.HS-ETS1-2').@en")
        C.alignmentLevel = make_datatype_prop(onto, "alignmentLevel", [C.StandardAlignment], int)
        C.alignmentLevel.comment.append("Strength of alignment on a 1-5 Likert scale.@en")

        # ── Cross-module closure: tighten M4 forward reference ──
        C.hasCompetency.range = [C.CompetencyDimension]

    print(f"  ✓ M5 Anchor: {_count(onto, 'classes')} classes, {_count(onto, 'object_properties')} obj props, {_count(onto, 'data_properties')} data props")
    return onto


# ═══════════════════════════════════════════════════════════════════════════════
# BUILD ALL + EXPORT
# ═══════════════════════════════════════════════════════════════════════════════

def build_all_tbox():
    """
    Build all 5 modules in the shared default_world.
    Returns the C (TBClasses) registry with all class references.
    """
    print("=" * 60)
    print("Building IE-PBL Ontology TBox (single shared World)")
    print("=" * 60)

    build_core()
    build_knowledge()
    build_process()
    build_team()
    build_anchor()

    print("=" * 60)
    world = default_world
    n_cls = len(list(world.classes()))
    n_op  = len(list(world.object_properties()))
    n_dp  = len(list(world.data_properties()))
    print(f"  Total: {n_cls} classes, {n_op} obj props, {n_dp} data props")
    return C


def _capture_list(graph, seed_set, list_node, bn_triples, visited):
    """Recursively capture all triples defining an RDF list starting from list_node."""
    from rdflib import BNode, RDF
    current = list_node
    while isinstance(current, BNode):
        cid = str(current)
        if cid in visited:
            break
        visited.add(cid)
        for t in bn_triples.get(cid, []):
            seed_set.add(t)
        # Move to rest — find the rdf:rest triple for this node
        rest_found = False
        for s2, p2, o2 in graph:
            if s2 == current and p2 == RDF.rest:
                current = o2
                rest_found = True
                break
        if not rest_found:
            break


def export_modules():
    """
    Export each module's TBox to a separate .ttl file by filtering the
    combined rdflib graph by namespace, with transitive blank-node closure.

    APPROACH (fixes the blank-node bug):
      1. First pass: collect candidate triples whose S/P/O matches the module IRI prefix.
      2. Second pass: collect ALL triples that define any blank node referenced
         from the candidate set (transitive closure), so that owl:equivalentClass [ ... ],
         owl:unionOf lists, owl:allDisjointClasses, owl:restriction, etc. are NOT split.
      3. BFS on blank nodes ensures deeply nested RDF lists (rdf:first/rdf:rest chains)
         are fully captured.
    """
    from rdflib import Graph, URIRef, RDF, RDFS, OWL, BNode
    import hashlib
    from collections import deque

    MODULE_PATHS["core"].parent.mkdir(parents=True, exist_ok=True)

    g = default_world.as_rdflib_graph()

    # Map module IRIs to file paths
    module_map = {
        MODULE_IRIS["core"]:      MODULE_PATHS["core"],
        MODULE_IRIS["knowledge"]: MODULE_PATHS["knowledge"],
        MODULE_IRIS["process"]:   MODULE_PATHS["process"],
        MODULE_IRIS["team"]:      MODULE_PATHS["team"],
        MODULE_IRIS["anchor"]:    MODULE_PATHS["anchor"],
    }

    # Build a lookup: for any blank node, which triples define it?
    blank_node_triples = {}  # BNode identifier -> list of (s,p,o) triples
    for s, p, o in g:
        if isinstance(s, BNode):
            bid = str(s)
            if bid not in blank_node_triples:
                blank_node_triples[bid] = []
            blank_node_triples[bid].append((s, p, o))

    # ── Namespace prefix bindings for readable Turtle output ──
    # Each module gets its own short prefix plus prefixes for all other modules
    # so cross-module references use prefix:LocalName instead of full IRIs.
    PREFIX_MAP = {
        "core":      "core",
        "knowledge": "kn",
        "process":   "proc",
        "team":      "team",
        "anchor":    "anchor",
    }

    for mod_iri, mod_path in module_map.items():
        mod_g = Graph()
        mod_base = mod_iri.replace(".ttl", "")

        # ── Pass 1: direct IRI-prefix matching ──
        seed_triples = set()
        seed_bnodes = set()

        for s, p, o in g:
            s_str = str(s)
            p_str = str(p)
            o_str = str(o) if not isinstance(o, URIRef) else str(o)

            include = (
                s_str.startswith(mod_base) or
                p_str.startswith(mod_base) or
                o_str.startswith(mod_base)
            )
            # type triples where the object (class) belongs to this module
            if not include and p == RDF.type:
                include = o_str.startswith(mod_base)

            if include:
                seed_triples.add((s, p, o))
                if isinstance(s, BNode):
                    seed_bnodes.add(str(s))
                if isinstance(o, BNode):
                    seed_bnodes.add(str(o))

        # ── Pass 2: transitive closure on blank nodes ──
        # BFS: for every blank node reachable from seed triples,
        # include all triples that define it (its outgoing edges).
        queue = deque(seed_bnodes)
        visited_bnodes = set(seed_bnodes)

        while queue:
            bid = queue.popleft()
            for triple in blank_node_triples.get(bid, []):
                seed_triples.add(triple)
                s2, p2, o2 = triple
                # If this triple references other blank nodes, traverse them too
                if isinstance(o2, BNode) and str(o2) not in visited_bnodes:
                    visited_bnodes.add(str(o2))
                    queue.append(str(o2))
                if isinstance(p2, BNode) and str(p2) not in visited_bnodes:
                    visited_bnodes.add(str(p2))
                    queue.append(str(p2))

        # ── Pass 3: capture orphan blank nodes used in OWL constructs ──
        # Some OWL constructs (AllDisjointClasses, AllDifferent) create
        # blank nodes that are NOT referenced by any named resource.
        # Find them by checking the members list for classes from this module.
        for s, p, o in g:
            if p == RDF.type and o == OWL.AllDisjointClasses:
                # AllDisjointClasses instance — check its owl:members list
                members_list = list(g.objects(s, OWL.members))
                for ml in members_list:
                    # Traverse the RDF list and check if any member class
                    # belongs to this module
                    current = ml
                    while current and isinstance(current, BNode):
                        for first_val in g.objects(current, RDF.first):
                            if isinstance(first_val, URIRef):
                                f_str = str(first_val)
                                if f_str.startswith(mod_base):
                                    # This AllDisjointClasses belongs to our module
                                    # Include the AllDisjointClasses node itself
                                    for t in blank_node_triples.get(str(s), []):
                                        seed_triples.add(t)
                                    # Include the list structure
                                    _capture_list(g, seed_triples, ml, blank_node_triples, visited_bnodes)
                                    break
                        rest = list(g.objects(current, RDF.rest))
                        if rest:
                            current = rest[0]
                            if isinstance(current, BNode) and str(current) not in visited_bnodes:
                                visited_bnodes.add(str(current))
                                for t in blank_node_triples.get(str(current), []):
                                    seed_triples.add(t)
                        else:
                            break

        # Add ontology declaration triple if the module has any triples
        for s, p, o in seed_triples:
            mod_g.add((s, p, o))

        # ── Add owl:imports declarations for cross-module references ──
        # Determine which modules this module depends on
        dep_map = {
            "core":      [],
            "knowledge": ["core"],
            "process":   ["core", "knowledge"],           # v3.0: removed "team" — resolves M3↔M4 cycle
            "team":      ["core", "knowledge", "process"],
            "anchor":    ["core", "knowledge", "process", "team"],
        }
        mod_key = None
        for key, path in MODULE_PATHS.items():
            if key != "ie-pbl" and path == mod_path:
                mod_key = key
                break
        if mod_key and mod_key in dep_map:
            mod_iri_uri = URIRef(MODULE_IRIS[mod_key])
            if (mod_iri_uri, RDF.type, OWL.Ontology) not in set(mod_g.triples((mod_iri_uri, RDF.type, OWL.Ontology))):
                mod_g.add((mod_iri_uri, RDF.type, OWL.Ontology))
            for dep_key in dep_map[mod_key]:
                dep_iri = URIRef(MODULE_IRIS[dep_key])
                mod_g.add((mod_iri_uri, OWL.imports, dep_iri))

        # ── Bind namespace prefixes for readable output ──
        # Bind the module's own prefix
        for key, prefix in PREFIX_MAP.items():
            ns = MODULE_IRIS[key] + "#"
            mod_g.bind(prefix, ns)
        # Also bind standard vocabularies
        mod_g.bind("owl", "http://www.w3.org/2002/07/owl#")
        mod_g.bind("rdfs", "http://www.w3.org/2000/01/rdf-schema#")
        mod_g.bind("rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns#")
        mod_g.bind("xsd", "http://www.w3.org/2001/XMLSchema#")

        mod_g.serialize(str(mod_path), format="turtle", base=IRI)
        md5 = hashlib.md5(mod_g.serialize(format="turtle").encode("utf-8")).hexdigest()
        n_axioms = len(mod_g)
        print(f"  ✓ {mod_path.name}: {n_axioms} triples (MD5: {md5[:8]}...)")

    return module_map


def export_ie_pbl_master():
    """Export ie-pbl.ttl with owl:imports declarations."""
    from rdflib import Graph, URIRef, Literal, Namespace, RDF, RDFS
    OWL_NS = Namespace("http://www.w3.org/2002/07/owl#")
    RDFS_NS = Namespace("http://www.w3.org/2000/01/rdf-schema#")

    g = Graph()
    master_iri = URIRef(IRI + "ie-pbl")
    g.add((master_iri, RDF.type, OWL_NS.Ontology))
    g.add((master_iri, RDFS_NS.label, Literal("IE-PBL Ontology", lang="en")))
    g.add((master_iri, RDFS_NS.comment, Literal(
        "Interdisciplinary Engineering Project-Based Learning Ontology. "
        "Multi-purpose semantic digital twin.", lang="en")))

    for mod_iri in MODULE_IRIS.values():
        g.add((master_iri, OWL_NS["imports"], URIRef(mod_iri)))

    path = str(MODULE_PATHS["ie-pbl"])
    g.serialize(path, format="turtle", base=IRI)
    print(f"  ✓ ie-pbl.ttl: {len(g)} triples (master ontology with imports)")

    return path


def validate_with_pellet():
    """Run Pellet reasoner and report consistency."""
    print("\nRunning Pellet reasoner on complete TBox...")
    try:
        sync_reasoner_pellet(infer_property_values=True, debug=0)
        print("✓ CONSISTENT — 0 inconsistencies found")
        return True
    except Exception as e:
        print(f"✗ INCONSISTENCY: {e}")
        return False


# ═══════════════════════════════════════════════════════════════════════════════
# UTILITY
# ═══════════════════════════════════════════════════════════════════════════════

def _count(onto, kind):
    """Count entities in an ontology."""
    if kind == "classes":
        return len(list(onto.classes()))
    elif kind == "object_properties":
        return len(list(onto.object_properties()))
    elif kind == "data_properties":
        return len(list(onto.data_properties()))
    return 0
