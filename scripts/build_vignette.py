#!/usr/bin/env python3
"""
build_vignette.py — Build the Team_Alpha Wind Turbine ABox Vignette.

Creates a detailed ABox instantiation of a single PBL team designing a wind turbine.
Includes:
  - 1 Project with DrivingQuestion, 5 Phases, ~15 Activities
  - 3 Learners, 1 Instructor, 6 VirtualAgents, 1 Team
  - ~20 DiscourseActions with utteranceText and timestamps
  - 3 InterdisciplinaryBridge instances
  - 1 InstructorIntervention (SafetyIntervention) instance
  - 6 PerformanceTrace instances with derivedFromEvent chains
  - 1 TeamState snapshot

Usage:
    python scripts/build_vignette.py
"""

import sys
import os
import datetime as dt
import json

sys.path.insert(0, os.path.dirname(__file__))

from owlready2 import *
from config import IRI, VIGNETTE_DIR, ONTO_DIR
from tbox import build_all_tbox, validate_with_pellet


def build_vignette(C):
    """Construct the Team_Alpha ABox in the default World."""
    # ── shorthand ──
    pbl = f"{IRI}vignette#"

    # ═════════════════════════════════════════════════════════════════
    # PROJECT & DRIVING QUESTION
    # ═════════════════════════════════════════════════════════════════
    proj = C.Project(pbl + "WindTurbine_Project")
    proj.hasTitle = ["Wind Turbine Design Challenge"]
    proj.hasDescription = [
        "Team Alpha designs and builds a small-scale wind turbine capable of "
        "generating enough electricity to light an LED, while meeting constraints "
        "on blade material, tower height, and structural stability."
    ]
    proj.startTime = [dt.datetime(2026, 3, 1, 9, 0, 0)]
    proj.endTime   = [dt.datetime(2026, 3, 15, 17, 0, 0)]

    # ═════════════════════════════════════════════════════════════════
    # PHASES & ACTIVITIES (using EiE framework for K-12 vignette)
    # ═════════════════════════════════════════════════════════════════
    # --- EiE_Ask Phase (⊑ ProblemScoping) ---
    ask_phase = C.EiE_Ask(pbl + "Ask_Phase_1")
    ask_phase.hasTitle = ["Ask: Understanding the Problem"]
    ask_phase.startTime = [dt.datetime(2026, 3, 1, 9, 0, 0)]
    ask_phase.endTime   = [dt.datetime(2026, 3, 3, 10, 30, 0)]
    proj.hasPhase.append(ask_phase)

    act_ask1 = C.Activity(pbl + "Activity_Ask_BrainstormNeeds")
    act_ask1.hasTitle = ["Brainstorm: What do we need to know?"]
    ask_phase.hasActivity.append(act_ask1)

    act_ask2 = C.Activity(pbl + "Activity_Ask_ResearchTurbines")
    act_ask2.hasTitle = ["Research real wind turbines (videos, articles)"]
    ask_phase.hasActivity.append(act_ask2)

    act_ask3 = C.Activity(pbl + "Activity_Ask_DefineConstraints")
    act_ask3.hasTitle = ["Define constraints: materials, size, cost limit"]
    ask_phase.hasActivity.append(act_ask3)

    # --- Imagine Phase ---
    imagine_phase = C.EiE_Imagine(pbl + "Imagine_Phase_1")
    imagine_phase.hasTitle = ["Imagine: Brainstorming Solutions"]
    imagine_phase.startTime = [dt.datetime(2026, 3, 3, 10, 30, 0)]
    imagine_phase.endTime   = [dt.datetime(2026, 3, 5, 11, 0, 0)]
    ask_phase.precedes.append(imagine_phase)
    proj.hasPhase.append(imagine_phase)

    act_img1 = C.Activity(pbl + "Activity_Imagine_SketchDesigns")
    act_img1.hasTitle = ["Sketch 3 different blade designs"]
    imagine_phase.hasActivity.append(act_img1)

    act_img2 = C.Activity(pbl + "Activity_Imagine_CompareDesigns")
    act_img2.hasTitle = ["Compare designs using constraint checklist"]
    imagine_phase.hasActivity.append(act_img2)

    # --- Plan Phase ---
    plan_phase = C.EiE_Plan(pbl + "Plan_Phase_1")
    plan_phase.hasTitle = ["Plan: Selecting the Design"]
    plan_phase.startTime = [dt.datetime(2026, 3, 5, 11, 0, 0)]
    plan_phase.endTime   = [dt.datetime(2026, 3, 8, 10, 0, 0)]
    imagine_phase.precedes.append(plan_phase)
    proj.hasPhase.append(plan_phase)

    act_plan1 = C.DesignActivity(pbl + "Activity_Plan_DrawBlueprint")
    act_plan1.hasTitle = ["Draw detailed blueprint with measurements"]
    plan_phase.hasActivity.append(act_plan1)

    act_plan2 = C.DesignActivity(pbl + "Activity_Plan_PrepMaterials")
    act_plan2.hasTitle = ["Prepare materials list & assign roles"]
    plan_phase.hasActivity.append(act_plan2)

    # --- Create Phase ---
    create_phase = C.EiE_Create(pbl + "Create_Phase_1")
    create_phase.hasTitle = ["Create: Building & Testing"]
    create_phase.startTime = [dt.datetime(2026, 3, 8, 10, 0, 0)]
    create_phase.endTime   = [dt.datetime(2026, 3, 12, 11, 0, 0)]
    plan_phase.precedes.append(create_phase)
    proj.hasPhase.append(create_phase)

    act_create1 = C.Activity(pbl + "Activity_Create_BuildBlades")
    act_create1.hasTitle = ["Build blade assembly"]
    create_phase.hasActivity.append(act_create1)

    act_create2 = C.Activity(pbl + "Activity_Create_AssembleTurbine")
    act_create2.hasTitle = ["Assemble tower, nacelle, and blades"]
    create_phase.hasActivity.append(act_create2)

    act_create3 = C.Activity(pbl + "Activity_Create_FirstTest")
    act_create3.hasTitle = ["First wind test: measure voltage output"]
    create_phase.hasActivity.append(act_create3)

    # --- Improve Phase ---
    improve_phase = C.EiE_Improve(pbl + "Improve_Phase_1")
    improve_phase.hasTitle = ["Improve: Iterating the Design"]
    improve_phase.startTime = [dt.datetime(2026, 3, 12, 11, 0, 0)]
    improve_phase.endTime   = [dt.datetime(2026, 3, 15, 16, 0, 0)]
    create_phase.precedes.append(improve_phase)
    proj.hasPhase.append(improve_phase)

    # Backtrack: improve → plan (simulates test-failure-driven recursion)
    improve_phase.backtracksTo.append(plan_phase)

    act_imp1 = C.Activity(pbl + "Activity_Improve_AnalyzeData")
    act_imp1.hasTitle = ["Analyze test data: voltage vs. blade angle"]
    improve_phase.hasActivity.append(act_imp1)

    act_imp2 = C.Activity(pbl + "Activity_Improve_RedesignBlades")
    act_imp2.hasTitle = ["Redesign blades for higher RPM"]
    improve_phase.hasActivity.append(act_imp2)

    act_imp3 = C.Activity(pbl + "Activity_Improve_FinalTest")
    act_imp3.hasTitle = ["Final wind tunnel test with optimized design"]
    improve_phase.hasActivity.append(act_imp3)
    # ═════════════════════════════════════════════════════════════════
    # TEAM & ACTORS
    # ═════════════════════════════════════════════════════════════════
    team = C.Team(pbl + "Team_Alpha")
    team.hasTitle = ["Team Alpha"]
    proj.hasTeam.append(team)

    # v3.0: Constraint with dynamic reasoning
    budget_constraint = C.Constraint(IRI + "vignette#" + "Constraint_Budget")
    budget_constraint.hasTitle = ["Budget: $100 max for materials"]
    budget_constraint.hasDescription = ["Total materials cost must not exceed $100 for the wind turbine project."]
    proj.hasConstraint.append(budget_constraint)
    budget_constraint.constraintViolationTriggers.append(plan_phase)

    # Learners
    alice = C.Learner(pbl + "Learner_Alice")
    alice.hasName = ["Alice"]
    team.hasTeamMember.append(alice)

    bob = C.Learner(pbl + "Learner_Bob")
    bob.hasName = ["Bob"]
    team.hasTeamMember.append(bob)

    carol = C.Learner(pbl + "Learner_Carol")
    carol.hasName = ["Carol"]
    team.hasTeamMember.append(carol)

    # v3.0: Deliverable instances with hooks for future quality assessment
    deliverable_turbine = C.Deliverable(IRI + "vignette#" + "Deliverable_Turbine")
    deliverable_turbine.hasTitle = ["Wind Turbine Prototype"]
    deliverable_turbine.deliverableType = ["prototype"]
    deliverable_turbine.isProducedBy.append(bob)
    deliverable_turbine.hasEvaluationCriterion = ["rubric.build-quality", "rubric.functionality"]
    act_create3.hasDeliverable.append(deliverable_turbine)

    deliverable_blueprint = C.Deliverable(IRI + "vignette#" + "Deliverable_Blueprint")
    deliverable_blueprint.hasTitle = ["Blade Design Blueprint"]
    deliverable_blueprint.deliverableType = ["model"]
    deliverable_blueprint.isProducedBy.append(carol)
    deliverable_blueprint.hasEvaluationCriterion = ["rubric.design-documentation"]
    act_plan1.hasDeliverable.append(deliverable_blueprint)


    # Instructor
    instructor = C.Instructor(pbl + "Instructor_DrWang")
    instructor.hasName = ["Dr. Wang"]

    # Roles
    pm_role = C.ProjectManager(pbl + "Role_ProjectManager")
    alice.playsRole.append(pm_role)
    builder_role = C.Builder(pbl + "Role_Builder")
    bob.playsRole.append(builder_role)
    prog_role = C.Programmer(pbl + "Role_Programmer")
    carol.playsRole.append(prog_role)

    # Virtual Agents
    proc_guide = C.ProceduralGuide(pbl + "Agent_ProceduralGuide")
    proc_guide.personaPrompt = [
        "You are a procedural coach. Guide the team step-by-step through the "
        "engineering design process. Keep instructions concrete and scaffolded."
    ]
    proc_guide.monitorsTeam.append(team)

    conc_expert = C.ConceptualExpert(pbl + "Agent_ConceptualExpert")
    conc_expert.personaPrompt = [
        "You are a domain expert in physics and engineering. Provide conceptual "
        "explanations about aerodynamics, structural mechanics, and circuits."
    ]
    conc_expert.monitorsTeam.append(team)

    meta_chall = C.MetacognitiveChallenger(pbl + "Agent_MetacognitiveChallenger")
    meta_chall.personaPrompt = [
        "You are a metacognitive coach. Ask reflective questions: 'Why do you "
        "think that worked?', 'What would you do differently next time?'"
    ]
    meta_chall.monitorsTeam.append(team)

    div_brain = C.DivergentBrainstormer(pbl + "Agent_DivergentBrainstormer")
    div_brain.personaPrompt = [
        "You are a creative ideation partner. Suggest wild ideas, analogies "
        "from nature, and unconventional approaches."
    ]
    div_brain.monitorsTeam.append(team)

    # Safety Monitor (v2.0 — 5th VirtualAgent subtype)
    safety_mon = C.SafetyMonitor(pbl + "Agent_SafetyMonitor")
    safety_mon.personaPrompt = [
        "You are a safety officer. Monitor physical and digital safety risks "
        "during PBL activities, especially prototyping and testing. Alert "
        "the instructor when safety protocols are violated or risky behaviors detected."
    ]
    safety_mon.monitorsTeam.append(team)

    # Affective Supporter (v2.1 — 6th VirtualAgent subtype; added after the
    # B1/B2 revision loop and instantiated here so its trigger rules can fire)
    affective_sup = C.AffectiveSupporter(pbl + "Agent_AffectiveSupporter")
    affective_sup.personaPrompt = [
        "You are an empathetic supporter. Acknowledge emotions, encourage "
        "persistence after setbacks, and help the team regulate affect — "
        "without redirecting the task or evaluating ideas."
    ]
    affective_sup.monitorsTeam.append(team)

    # ═════════════════════════════════════════════════════════════════
    # KNOWLEDGE: Concepts, Skills, Domain Boundaries
    # ═════════════════════════════════════════════════════════════════
    # Domains
    domain_physics = C.DomainBoundary(pbl + "Domain_Physics")
    domain_physics.hasTitle = ["Physics"]
    domain_engineering = C.DomainBoundary(pbl + "Domain_Engineering")
    domain_engineering.hasTitle = ["Engineering"]

    # Concepts
    bernoulli = C.Concept(pbl + "Concept_Bernoulli")
    bernoulli.hasTitle = ["Bernoulli's Principle"]
    bernoulli.hasDefinition = [
        "As the speed of a fluid increases, the pressure within the fluid decreases."
    ]
    bernoulli.belongsToDomain.append(domain_physics)

    torque = C.Concept(pbl + "Concept_Torque")
    torque.hasTitle = ["Torque"]
    torque.hasDefinition = [
        "A measure of the force that causes an object to rotate about an axis."
    ]
    torque.belongsToDomain.append(domain_physics)

    gear_ratio = C.Concept(pbl + "Concept_GearRatio")
    gear_ratio.hasTitle = ["Gear Ratio"]
    gear_ratio.hasDefinition = [
        "The ratio of the number of teeth on two meshing gears, determining "
        "speed and torque multiplication."
    ]
    gear_ratio.belongsToDomain.append(domain_engineering)

    # Skills
    cad_modeling = C.Skill(pbl + "Skill_CADModeling")
    cad_modeling.hasTitle = ["CAD Modeling"]
    cad_modeling.hasProficiencyLevel = [2]
    cad_modeling.requiresConcept.append(gear_ratio)

    data_analysis = C.Skill(pbl + "Skill_DataAnalysis")
    data_analysis.hasTitle = ["Data Analysis"]
    data_analysis.hasProficiencyLevel = [3]

    # ═════════════════════════════════════════════════════════════════
    # DISCOURSE ACTIONS (micro-level discourse with timestamps)
    # ═════════════════════════════════════════════════════════════════
    t0 = dt.datetime(2026, 3, 9, 10, 15, 0)

    # ═════════════════════════════════════════════════════════════════
    # S2D SCIENTIFIC INVESTIGATION PHASE + INQUIRY ACTIVITY
    # ═════════════════════════════════════════════════════════════════
    sci_phase = C.FiveE_Explore(pbl + "Science_FiveE_Explore_1")
    sci_phase.hasTitle = ["5E Explore: Aerodynamics Experiment"]
    sci_phase.startTime = [dt.datetime(2026, 3, 4, 9, 0, 0)]
    sci_phase.endTime   = [dt.datetime(2026, 3, 7, 10, 0, 0)]
    proj.hasPhase.append(sci_phase)

    # v3.0: Per-student phase tracking
    alice.learnerCurrentPhase.append(create_phase)
    bob.learnerCurrentPhase.append(create_phase)
    carol.learnerCurrentPhase.append(sci_phase)


    act_inquiry = C.InquiryActivity(pbl + "Activity_Inquiry_WindTunnelTest")
    act_inquiry.hasTitle = ["Wind tunnel experiment: measure voltage vs. blade pitch"]
    sci_phase.hasActivity.append(act_inquiry)

    # S2D scientific discourse actions
    da_hyp = C.HypothesisProposing(pbl + "DA_S2D_Hypothesis")
    da_hyp.utteranceText = [
        "I think a steeper blade angle will generate more voltage because "
        "the wind hits the blade surface more directly, transferring more energy."
    ]
    da_hyp.timestamp = [dt.datetime(2026, 3, 4, 9, 30, 0)]
    da_hyp.occursInPhase.append(sci_phase)
    da_hyp.isAttributedTo.append(carol)

    da_evid = C.EvidenceAnalyzing(pbl + "DA_S2D_Evidence")
    da_evid.utteranceText = [
        "Look at the data: at 15 degrees we got 2.1V, at 30 degrees 2.8V, "
        "but at 45 degrees it dropped to 2.3V. There's an optimal point somewhere."
    ]
    da_evid.timestamp = [dt.datetime(2026, 3, 4, 10, 15, 0)]
    da_evid.occursInPhase.append(sci_phase)
    da_evid.isAttributedTo.append(alice)

    da_princ = C.PrincipleFormulating(pbl + "DA_S2D_Principle")
    da_princ.utteranceText = [
        "The scientific rule we discovered: there's an optimal pitch angle "
        "around 30 degrees where efficiency peaks. Past that, flow separation "
        "starts happening and voltage drops — just like Bernoulli predicted."
    ]
    da_princ.timestamp = [dt.datetime(2026, 3, 4, 10, 45, 0)]
    da_princ.occursInPhase.append(sci_phase)
    da_princ.isAttributedTo.append(carol)
    da_princ.referencesConcept.append(bernoulli)

    # S2D Bridge: the principle directly informs the blade-making activity
    da_princ.informsDesign.append(act_plan1)  # RDF: plan the blade angle based on principle

    # Link S2D discourse chain for transitive SPARQL traversal
    da_hyp.isFollowedByAction.append(da_evid)
    da_evid.isFollowedByAction.append(da_princ)

    # ═════════════════════════════════════════════════════════════════
    # EXISTING DISCOURSE ACTIONS
    # ═════════════════════════════════════════════════════════════════

    da1 = C.HelpSeeking(pbl + "DA_01")
    da1.utteranceText = ["How do we attach the blades to the shaft securely?"]
    da1.timestamp = [t0]
    da1.occursInPhase.append(create_phase)
    da1.isAttributedTo.append(bob)

    da2 = C.FailureReporting(pbl + "DA_02")
    da2.utteranceText = ["The blades keep falling off when we spin the motor!"]
    da2.timestamp = [t0 + dt.timedelta(minutes=15)]
    da2.occursInPhase.append(create_phase)
    da2.isAttributedTo.append(alice)

    da3 = C.PeerArgumentation(pbl + "DA_03")
    da3.utteranceText = [
        "I think three curved blades will catch more wind than four flat ones. "
        "Real wind turbines use three blades, and they're curved like airplane wings."
    ]
    da3.timestamp = [t0 + dt.timedelta(minutes=25)]
    da3.occursInPhase.append(imagine_phase)
    da3.isAttributedTo.append(carol)
    da3.referencesConcept.append(bernoulli)

    da4 = C.ProcessConfusion(pbl + "DA_04")
    da4.utteranceText = [
        "Wait, should we test first or fix the wobble first? I'm not sure "
        "what the next step is."
    ]
    da4.timestamp = [t0 + dt.timedelta(minutes=35)]
    da4.occursInPhase.append(create_phase)
    da4.isAttributedTo.append(bob)

    da5 = C.KnowledgeSharing(pbl + "DA_05")
    da5.utteranceText = [
        "I read that the angle of the blades matters a lot. They call it "
        "'pitch angle' — if it's too steep, the wind just pushes the blade "
        "down instead of spinning it."
    ]
    da5.timestamp = [t0 + dt.timedelta(minutes=40)]
    da5.occursInPhase.append(create_phase)
    da5.isAttributedTo.append(carol)

    da6 = C.HelpSeeking(pbl + "DA_06")
    da6.utteranceText = [
        "Can someone explain why the voltage drops when we connect the LED directly?"
    ]
    da6.timestamp = [t0 + dt.timedelta(hours=1)]
    da6.occursInPhase.append(create_phase)
    da6.isAttributedTo.append(alice)

    da7 = C.PlanningUtterance(pbl + "DA_07")
    da7.utteranceText = [
        "OK, let's plan: Bob will reinforce the tower, Alice will adjust the "
        "blade pitch, and I'll rewire the circuit. Then we test again in 20 minutes."
    ]
    da7.timestamp = [t0 + dt.timedelta(hours=1, minutes=20)]
    da7.occursInPhase.append(improve_phase)
    da7.isAttributedTo.append(carol)

    da8 = C.IdeaGeneration(pbl + "DA_08")
    da8.utteranceText = [
        "What if we make the blades out of balsa wood instead of cardboard? "
        "It's lighter, so the wind can spin it faster. And we could carve "
        "an airfoil shape like a real wing."
    ]
    da8.timestamp = [t0 + dt.timedelta(days=1)]
    da8.occursInPhase.append(imagine_phase)
    da8.isAttributedTo.append(bob)

    da9 = C.FailureReporting(pbl + "DA_09")
    da9.utteranceText = [
        "The whole turbine just fell over! The base is too light. When the "
        "fan was on high speed, the torque twisted the tower right off the table."
    ]
    da9.timestamp = [t0 + dt.timedelta(days=1, hours=2)]
    da9.occursInPhase.append(create_phase)
    da9.isAttributedTo.append(alice)
    da9.referencesConcept.append(torque)

    da10 = C.PeerArgumentation(pbl + "DA_10")
    da10.utteranceText = [
        "Adding weight to the base will reduce vibration, but if we make it "
        "TOO heavy the whole thing becomes hard to move. We need to balance "
        "stability with portability."
    ]
    da10.timestamp = [t0 + dt.timedelta(days=2)]
    da10.occursInPhase.append(improve_phase)
    da10.isAttributedTo.append(carol)

    # More discourse — HelpSeeking during improve
    da11 = C.HelpSeeking(pbl + "DA_11")
    da11.utteranceText = [
        "How do I calculate the gear ratio between our turbine shaft and the motor?"
    ]
    da11.timestamp = [t0 + dt.timedelta(days=2, hours=1)]
    da11.occursInPhase.append(improve_phase)
    da11.isAttributedTo.append(bob)

    da12 = C.KnowledgeSharing(pbl + "DA_12")
    da12.utteranceText = [
        "If the big gear has 40 teeth and the small one has 10, the ratio "
        "is 4:1 — so the motor spins 4 times for every 1 turn of the turbine."
    ]
    da12.timestamp = [t0 + dt.timedelta(days=2, hours=1, minutes=10)]
    da12.occursInPhase.append(improve_phase)
    da12.isAttributedTo.append(carol)

    # ═════════════════════════════════════════════════════════════════
    # v2.1 NEW DISCOURSE ACTIONS
    # ═════════════════════════════════════════════════════════════════
    # SocialBonding: Bob says something light-hearted during Create
    da_social = C.SocialBonding(pbl + "DA_SocialBonding_01")
    da_social.utteranceText = [
        "This turbine is starting to look like a giant desk fan! "
        "Maybe we can use it to cool down our lunch after class."
    ]
    da_social.timestamp = [t0 + dt.timedelta(minutes=30)]
    da_social.occursInPhase.append(create_phase)
    da_social.isAttributedTo.append(bob)

    # Disagreement: Bob disagrees with material choice during Create
    da_disagree = C.Disagreement(pbl + "DA_Disagreement_01")
    da_disagree.utteranceText = [
        "I'm not so sure about balsa wood — it might be too brittle. "
        "I think we need something stronger for the blades."
    ]
    da_disagree.timestamp = [t0 + dt.timedelta(minutes=45)]
    da_disagree.occursInPhase.append(create_phase)
    da_disagree.isAttributedTo.append(bob)

    # Agreement: Alice agrees with the 30° design decision during Improve
    da_agree = C.Agreement(pbl + "DA_Agreement_01")
    da_agree.utteranceText = [
        "Yeah, I agree — 30 degrees seems like the sweet spot from the data."
    ]
    da_agree.timestamp = [t0 + dt.timedelta(days=2, hours=2, minutes=5)]
    da_agree.occursInPhase.append(improve_phase)
    da_agree.isAttributedTo.append(alice)

    # PeerTutoring: Carol explains gear ratio to Bob during Improve
    da_tutor = C.PeerTutoring(pbl + "DA_PeerTutoring_01")
    da_tutor.utteranceText = [
        "Let me show you how the gear ratio works. See, when the big gear "
        "turns once, the small gear has to turn four times. That's why our "
        "turbine spins the motor faster than if we connected them directly."
    ]
    da_tutor.timestamp = [t0 + dt.timedelta(days=2, hours=1, minutes=15)]
    da_tutor.occursInPhase.append(improve_phase)
    da_tutor.isAttributedTo.append(carol)

    # DesignJustification: Carol explicitly connects S2D principle to design decision
    da_dj = C.DesignJustification(pbl + "DA_DesignJustification_01")
    da_dj.utteranceText = [
        "Based on our wind tunnel experiment, we know 30° blade pitch gives "
        "the highest voltage. Let's set the blades at 30° for our final "
        "design — the science proves it's the most efficient angle."
    ]
    da_dj.timestamp = [t0 + dt.timedelta(days=2, hours=2)]
    da_dj.occursInPhase.append(improve_phase)
    da_dj.isAttributedTo.append(carol)
    # S2D link: this justification informs the redesign activity
    da_dj.informsDesign.append(act_imp2)
    # The scientific principle (da_princ) justifies this design decision
    da_princ.justifiesDecision.append(da_dj)

    # v3.0: ConstraintReasoningAction — Bob reasons about budget constraint
    da_constraint = C.ConstraintReasoningAction(IRI + "vignette#" + "DA_ConstraintReasoning_01")
    da_constraint.utteranceText = [
        "Balsa wood costs $15 per sheet and we need 4 sheets — that's $60 already. "
        "If we use cardboard for the tower base instead of plywood, we can stay "
        "under our $100 budget and still have enough for the motor."
    ]
    da_constraint.timestamp = [t0 + dt.timedelta(days=1, hours=1)]
    da_constraint.occursInPhase.append(create_phase)
    da_constraint.isAttributedTo.append(bob)
    da_constraint.referencesConcept.append(gear_ratio)

    # v3.0: Cross-team discourse — Carol references another team's work
    da_cross_team = C.PeerArgumentation(IRI + "vignette#" + "DA_CrossTeam_01")
    da_cross_team.utteranceText = [
        "Team Beta used a gearbox from an old toy car and got much higher RPM. "
        "Maybe we should try something similar instead of direct drive."
    ]
    da_cross_team.timestamp = [t0 + dt.timedelta(days=2, hours=3)]
    da_cross_team.occursInPhase.append(improve_phase)
    da_cross_team.isAttributedTo.append(carol)
    da_cross_team.directedToTeam.append(team)
    da_cross_team.referencesTeamWork.append(team)

    # ═════════════════════════════════════════════════════════════════
    # NONVERBAL ACTIONS (v2.0 — complementing DiscourseAction)
    # ═════════════════════════════════════════════════════════════════
    nva_proto = C.PhysicalPrototyping(pbl + "NVA_01_Bob_BuildBlades")
    nva_proto.occursInPhase.append(create_phase)
    nva_proto.isAttributedTo.append(bob)
    nva_proto.timestamp = [t0 + dt.timedelta(minutes=5)]

    nva_tool = C.ToolSharing(pbl + "NVA_02_Carol_ShareGlueGun")
    nva_tool.occursInPhase.append(create_phase)
    nva_tool.isAttributedTo.append(carol)
    nva_tool.timestamp = [t0 + dt.timedelta(minutes=20)]
    nva_proto.hasModality = ["physical"]
    nva_tool.hasModality = ["physical"]

    # v2.1: Gesturing & Nodding
    nva_gesture = C.Gesturing(pbl + "NVA_03_Carol_GestureAngle")
    nva_gesture.occursInPhase.append(create_phase)
    nva_gesture.isAttributedTo.append(carol)
    nva_gesture.timestamp = [t0 + dt.timedelta(minutes=10)]
    nva_gesture.hasModality = ["gestural"]

    nva_nod = C.Nodding(pbl + "NVA_04_Alice_NodAgree")
    nva_nod.occursInPhase.append(create_phase)
    nva_nod.isAttributedTo.append(alice)
    nva_nod.timestamp = [t0 + dt.timedelta(minutes=12)]
    nva_nod.hasModality = ["gestural"]

    # ═════════════════════════════════════════════════════════════════
    # INTERDISCIPLINARY BRIDGES
    # ═════════════════════════════════════════════════════════════════
    bridge1 = C.AnalogyBridge(pbl + "Bridge_Analogy_AirfoilBlades")
    bridge1.hasTitle = ["Airfoil → Wind Turbine Blade Analogy"]
    bridge1.bridgesDomain.append(domain_physics)
    bridge1.bridgesDomain.append(domain_engineering)
    bridge1.linksConcept.append(bernoulli)
    bridge1.generatedInActivity.append(act_img1)

    bridge2 = C.IntegrationBridge(pbl + "Bridge_Integration_TorqueGearRatio")
    bridge2.hasTitle = ["Torque + Gear Ratio Integration"]
    bridge2.bridgesDomain.append(domain_physics)
    bridge2.bridgesDomain.append(domain_engineering)
    bridge2.linksConcept.append(torque)
    bridge2.linksConcept.append(gear_ratio)
    bridge2.generatedInActivity.append(act_imp1)

    # v3.0: boundaryCrossingStage and bridgeComplexity
    bridge1.boundaryCrossingStage = ["coordination"]
    bridge1.bridgeComplexity = [2]
    bridge2.boundaryCrossingStage = ["reflection"]
    bridge2.bridgeComplexity = [2]

    # v3.0: ValuePerspective
    community_perspective = C.ValuePerspective(IRI + "vignette#" + "ValuePerspective_Community")
    community_perspective.hasTitle = ["Community Environmental Concern"]
    community_perspective.hasDescription = [
        "Local residents are concerned about noise levels and visual impact of wind turbines."
    ]

    # ═════════════════════════════════════════════════════════════════
    # INSTRUCTOR INTERVENTIONS
    # ═════════════════════════════════════════════════════════════════
    # SafetyIntervention: Instructor overrides ProceduralGuide on blade safety
    intervention_safety = C.SafetyIntervention(pbl + "Intervention_Safety_BladeAssembly")
    intervention_safety.hasTitle = ["Safety Intervention: Blade Assembly Protocol"]
    intervention_safety.overridesAgent.append(proc_guide)
    # Performed by Instructor Dr. Wang during the Create phase when students
    # were assembling blades with sharp tools — instructor steps in to override
    # the ProceduralGuide's recommendation and enforce safety protocols.

    # ═════════════════════════════════════════════════════════════════
    # PERFORMANCE TRACES (with derivedFromEvent data lineage)
    # ═════════════════════════════════════════════════════════════════
    # Trace 1: Alice reports failure → evidence for EngineeringThinking
    trace1 = C.PerformanceTrace(pbl + "Trace_01_Alice_FailureReport")
    trace1.competencyScore = [0.60]
    trace1.recordedAt = [dt.datetime(2026, 3, 9, 10, 30, 0)]
    trace1.tracesCompetency.append(C.EngineeringThinking)
    trace1.isGeneratedByLearner.append(alice)
    trace1.derivedFromEvent.append(da2)

    # Trace 2: Carol uses peer argumentation → evidence for CollaborativeTeamwork
    trace2 = C.PerformanceTrace(pbl + "Trace_02_Carol_PeerArg")
    trace2.competencyScore = [0.80]
    trace2.recordedAt = [dt.datetime(2026, 3, 9, 10, 45, 0)]
    trace2.tracesCompetency.append(C.CollaborativeTeamwork)
    trace2.isGeneratedByLearner.append(carol)
    trace2.derivedFromEvent.append(da3)

    # Trace 3: Carol demonstrates interdisciplinary connections
    trace3 = C.PerformanceTrace(pbl + "Trace_03_Carol_Interdisciplinary")
    trace3.competencyScore = [0.85]
    trace3.recordedAt = [dt.datetime(2026, 3, 12, 14, 0, 0)]
    trace3.tracesCompetency.append(C.InterdisciplinaryIntegration)
    trace3.isGeneratedByLearner.append(carol)
    trace3.derivedFromEvent.append(da5)

    # Trace 4: Bob's idea generation → evidence for EngineeringThinking
    trace4 = C.PerformanceTrace(pbl + "Trace_04_Bob_IdeaGen")
    trace4.competencyScore = [0.70]
    trace4.recordedAt = [dt.datetime(2026, 3, 10, 10, 0, 0)]
    trace4.tracesCompetency.append(C.EngineeringThinking)
    trace4.isGeneratedByLearner.append(bob)
    trace4.derivedFromEvent.append(da8)

    # Trace 5: Alice's failure analysis with torque concept → EngineeringThinking
    trace5 = C.PerformanceTrace(pbl + "Trace_05_Alice_ConceptFailure")
    trace5.competencyScore = [0.75]
    trace5.recordedAt = [dt.datetime(2026, 3, 10, 12, 0, 0)]
    trace5.tracesCompetency.append(C.EngineeringThinking)
    trace5.isGeneratedByLearner.append(alice)
    trace5.derivedFromEvent.append(da9)

    # Trace 6: Carol's planning → CollaborativeTeamwork
    trace6 = C.PerformanceTrace(pbl + "Trace_06_Carol_Planning")
    trace6.competencyScore = [0.82]
    trace6.recordedAt = [dt.datetime(2026, 3, 12, 17, 0, 0)]
    trace6.tracesCompetency.append(C.CollaborativeTeamwork)
    trace6.isGeneratedByLearner.append(carol)
    trace6.derivedFromEvent.append(da7)

    # Trace_07: Bob's idea generation → CreativityAndInnovation
    # derivedFromEvent points to DA_08 (IdeaGeneration) — ECD evidence chain
    trace7 = C.PerformanceTrace(pbl + "Trace_07_Bob_Creativity")
    trace7.competencyScore = [0.78]
    trace7.recordedAt = [dt.datetime(2026, 3, 10, 10, 0, 0)]
    trace7.tracesCompetency.append(C.CreativityAndInnovation)
    trace7.isGeneratedByLearner.append(bob)
    trace7.derivedFromEvent.append(da8)

    # Reflection: Carol's analysis after the first test failure drives backtrack
    reflection_carol = C.Reflection(pbl + "Reflection_01_Carol_TestFailure")
    reflection_carol.reflectionText = [
        "After the first test failed, I realized we needed to reconsider our "
        "blade design approach. The materials we chose were too heavy, and "
        "we didn't account for proper torque distribution. Next iteration "
        "we should test blade pitch angles more systematically before building."
    ]

    # Trace_08: Carol's metacognitive reflection → MetacognitiveSelfRegulation
    trace8 = C.PerformanceTrace(pbl + "Trace_08_Carol_Metacognition")
    trace8.competencyScore = [0.83]
    trace8.recordedAt = [dt.datetime(2026, 3, 12, 17, 0, 0)]
    trace8.tracesCompetency.append(C.MetacognitiveSelfRegulation)
    trace8.isGeneratedByLearner.append(carol)
    trace8.derivedFromEvent.append(reflection_carol)

    # ═════════════════════════════════════════════════════════════════
    # COMPETENCY PROFILES (aggregated traces)
    # ═════════════════════════════════════════════════════════════════
    profile_alice = C.CompetencyProfile(pbl + "Profile_Alice")
    profile_alice.hasTitle = ["Alice's Competency Profile"]
    profile_alice.aggregatesTrace.append(trace1)
    profile_alice.aggregatesTrace.append(trace5)
    alice.hasCompetencyProfile.append(profile_alice)

    profile_carol = C.CompetencyProfile(pbl + "Profile_Carol")
    profile_carol.hasTitle = ["Carol's Competency Profile"]
    profile_carol.aggregatesTrace.append(trace2)
    profile_carol.aggregatesTrace.append(trace3)
    profile_carol.aggregatesTrace.append(trace6)
    carol.hasCompetencyProfile.append(profile_carol)

    profile_bob = C.CompetencyProfile(pbl + "Profile_Bob")
    profile_bob.hasTitle = ["Bob's Competency Profile"]
    profile_bob.aggregatesTrace.append(trace4)
    bob.hasCompetencyProfile.append(profile_bob)

    # ═════════════════════════════════════════════════════════════════
    # TEAM STATE (Analytics Dashboard snapshot)
    # ═════════════════════════════════════════════════════════════════
    ts = C.TeamState(pbl + "TeamState_Snapshot_Mar10")
    ts.collaborationIndex = [0.72]
    team.hasTeamState.append(ts)
    ts.snapshotTime = [dt.datetime(2026, 3, 10, 10, 0, 0)]

    collab_ind = C.CollaborationIndicator(pbl + "Indicator_Collab_Participation")
    collab_ind.indicatorValue = [0.72]
    collab_ind.hasTitle = ["Participation Equity Index"]

    process_ind = C.ProcessIndicator(pbl + "Indicator_Process_Iterations")
    process_ind.indicatorValue = [0.65]
    process_ind.hasTitle = ["Design Iteration Progress"]

    ts.hasAnalyticsIndicator.append(collab_ind)
    ts.hasAnalyticsIndicator.append(process_ind)

    # ═════════════════════════════════════════════════════════════════
    # v2.1: Second TeamState snapshot (time-series support)
    # ═════════════════════════════════════════════════════════════════
    ts2 = C.TeamState(pbl + "TeamState_Snapshot_Mar12")
    ts2.collaborationIndex = [0.78]
    ts2.snapshotTime = [dt.datetime(2026, 3, 12, 14, 0, 0)]
    team.hasTeamState.append(ts2)

    collab_ind2 = C.CollaborationIndicator(pbl + "Indicator_Collab_Participation_Mar12")
    collab_ind2.indicatorValue = [0.78]
    collab_ind2.hasTitle = ["Participation Equity Index"]

    process_ind2 = C.ProcessIndicator(pbl + "Indicator_Process_Iterations_Mar12")
    process_ind2.indicatorValue = [0.82]
    process_ind2.hasTitle = ["Design Iteration Progress"]

    ts2.hasAnalyticsIndicator.append(collab_ind2)
    ts2.hasAnalyticsIndicator.append(process_ind2)

    # ═════════════════════════════════════════════════════════════════
    # v2.1: Iteration instances (design-test-redesign micro-cycles)
    # ═════════════════════════════════════════════════════════════════

    # ── Iteration 1: Build & Test (Create phase — first fix attempt) ──
    iter_1 = C.Iteration(pbl + "Iteration_01_BuildTest")
    iter_1.iterationNumber = [1]
    iter_1.iterationTriggeredBy.append(da2)
    da2.triggersIteration.append(iter_1)
    iter_1.occursWithinProcess.append(create_phase)

    iter_outcome_1 = C.Failure(pbl + "IterOutcome_01_Failure")
    iter_1.hasIterationOutcome.append(iter_outcome_1)
    iter_outcome_1.isOutcomeOfIteration.append(iter_1)

    # Sub-iteration: quick fix attachment attempt
    iter_1a = C.Iteration(pbl + "Iteration_01a_FixAttachment")
    iter_1a.iterationNumber = [1]
    iter_1.hasSubIteration.append(iter_1a)
    iter_1a.isSubIterationOf.append(iter_1)

    iter_outcome_1a = C.PartialSuccess(pbl + "IterOutcome_01a_PartialSuccess")
    iter_1a.hasIterationOutcome.append(iter_outcome_1a)
    iter_outcome_1a.isOutcomeOfIteration.append(iter_1a)

    # ── Iteration 2: Structural Redesign (torque failure triggered) ──
    iter_2 = C.Iteration(pbl + "Iteration_02_Redesign")
    iter_2.iterationNumber = [2]
    iter_2.iterationTriggeredBy.append(da9)
    da9.triggersIteration.append(iter_2)
    iter_2.occursWithinProcess.append(create_phase)

    iter_outcome_2 = C.PartialSuccess(pbl + "IterOutcome_02_PartialSuccess")
    iter_2.hasIterationOutcome.append(iter_outcome_2)
    iter_outcome_2.isOutcomeOfIteration.append(iter_2)

    # ── Iteration 3: Optimize (scientific evidence triggered) ──
    iter_3 = C.Iteration(pbl + "Iteration_03_Optimize")
    iter_3.iterationNumber = [3]
    iter_3.iterationTriggeredBy.append(da_princ)
    da_princ.triggersIteration.append(iter_3)
    iter_3.occursWithinProcess.append(create_phase)

    iter_outcome_3 = C.Success(pbl + "IterOutcome_03_Success")
    iter_3.hasIterationOutcome.append(iter_outcome_3)
    iter_outcome_3.isOutcomeOfIteration.append(iter_3)

    return {
        "project": proj,
        "team": team,
        "learners": [alice, bob, carol],
        "agents": [proc_guide, conc_expert, meta_chall, div_brain, safety_mon],
        "discourse_actions": [da1, da2, da3, da4, da5, da6, da7, da8, da9, da10, da11, da12,
                              da_social, da_disagree, da_agree, da_tutor, da_dj, da_constraint, da_cross_team],
        "nonverbal_actions": [nva_proto, nva_tool, nva_gesture, nva_nod],
        "interventions": [intervention_safety],
        "traces": [trace1, trace2, trace3, trace4, trace5, trace6, trace7, trace8],
        "bridges": [bridge1, bridge2],
        "reflections": [reflection_carol],
        "team_state_snapshots": [ts, ts2],
        "deliverables": [deliverable_turbine, deliverable_blueprint],
        "value_perspectives": [community_perspective],
        "constraints": [budget_constraint],
    }


def export_vignette_graph():
    """Export the ABox vignette as a standalone Turtle file."""
    from rdflib import Graph, URIRef

    g = default_world.as_rdflib_graph()

    # Filter: only keep triples where the subject is a vignette individual
    vignette_g = Graph()
    vignette_base = f"{IRI}vignette#"

    for s, p, o in g:
        s_str = str(s)
        if vignette_base in s_str:
            vignette_g.add((s, p, o))

    path = VIGNETTE_DIR / "vignette-wind-turbine.ttl"
    path.parent.mkdir(parents=True, exist_ok=True)
    vignette_g.serialize(str(path), format="turtle", base=IRI)
    print(f"  ✓ Vignette exported: {path} ({len(vignette_g)} triples)")
    return path


def main():
    print("=" * 60)
    print("Building IE-PBL Ontology TBox + Team_Alpha ABox Vignette")
    print("=" * 60)

    # 1. Build TBox
    C = build_all_tbox()

    # 2. Build ABox
    print("\nBuilding Team_Alpha Vignette ABox...")
    abox = build_vignette(C)

    n_ind = len(list(default_world.individuals()))
    print(f"  ✓ ABox: {n_ind} individuals created")
    print(f"    - {len(abox['learners'])} learners")
    print(f"    - {len(abox['agents'])} virtual agents")
    print(f"    - {len(abox['discourse_actions'])} discourse actions")
    print(f"    - {len(abox['interventions'])} instructor interventions")
    print(f"    - {len(abox['traces'])} performance traces")
    print(f"    - {len(abox['bridges'])} interdisciplinary bridges")

    # 3. Validate TBox + ABox
    ok = validate_with_pellet()
    if not ok:
        print("\n❌ VALIDATION FAILED")
        sys.exit(1)

    # 4. Export vignette
    export_vignette_graph()

    print("\n✅ Vignette build complete — TBox + ABox consistent")


if __name__ == "__main__":
    main()
