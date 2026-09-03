#!/usr/bin/env python3
"""
build_sparql.py — Competency Questions (CQ) verification via SPARQL.

Executes 5 SPARQL queries against the TBox + ABox vignette to verify the
ontology's information retrieval capabilities:

  CQ1: Discourse timeline for Create phase (with triggered agents)
  CQ2: Performance lineage for Alice (complete evidence chain)
  CQ3: Interdisciplinary bridges detected in the project
  CQ4: Agent trigger summary — which agents responded to what
  CQ5: S2D cognitive pathway (Informed Design end-to-end trace)

Usage:
    python scripts/build_sparql.py
"""

import sys
import os
import json

sys.path.insert(0, os.path.dirname(__file__))

from owlready2 import *
from config import IRI, QUERIES_DIR
from tbox import build_all_tbox
from build_vignette import build_vignette


def run_sparql_cqs():
    """Run 4 Competency Questions and return results."""
    from rdflib import Graph, URIRef, Literal, RDF, RDFS

    g = default_world.as_rdflib_graph()

    ns = IRI
    NS = {
        "rdf":  "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
        "core": ns + "module-core.ttl#",
        "know": ns + "module-knowledge.ttl#",
        "proc": ns + "module-process.ttl#",
        "team": ns + "module-team.ttl#",
        "anch": ns + "module-anchor.ttl#",
    }

    results = {}

    # ═════════════════════════════════════════════════════════════════
    # CQ1: Discourse Timeline for Create Phase
    # "Retrieve all discourse actions in the Create phase, ordered by
    #  timestamp, showing the learner, action type, agent triggered,
    #  and referenced concept."
    # ═════════════════════════════════════════════════════════════════
    cq1 = g.query("""
        SELECT ?timestamp ?learnerName ?actionType ?utterance ?agentType
        WHERE {
            ?phase a core:Implementation .
            ?da proc:occursInPhase ?phase ;
                proc:timestamp ?timestamp ;
                proc:isAttributedTo ?learner .
            ?da a ?actionTypeClass .
            ?learner team:hasName ?learnerName .
            OPTIONAL { ?da proc:utteranceText ?utterance }
            OPTIONAL {
                ?da anch:triggersAgent ?agent .
                ?agent a ?agentClass
            }
            BIND(REPLACE(STR(?actionTypeClass), ".*#", "") AS ?actionType)
            BIND(COALESCE(REPLACE(STR(?agentClass), ".*#", ""), "-") AS ?agentType)
        }
        ORDER BY ?timestamp
    """, initNs=NS)

    results["CQ1_discourse_timeline"] = []
    for row in cq1:
        results["CQ1_discourse_timeline"].append({
            "timestamp": str(row.timestamp),
            "learner": str(row.learnerName),
            "action": str(row.actionType),
            "utterance": str(row.utterance)[:60] if row.utterance else "",
            "agent_triggered": str(row.agentType) if row.agentType else "-",
        })

    # ═════════════════════════════════════════════════════════════════
    # CQ2: Performance Lineage for Alice
    # "For learner Alice, show all performance traces with their
    #  competency dimensions, scores, and the originating PBL event
    #  (discourse action) that the trace was derived from."
    # ═════════════════════════════════════════════════════════════════
    cq2 = g.query("""
        SELECT ?competency ?score ?timestamp ?utterance ?eventType
        WHERE {
            ?learner team:hasName "Alice" .
            ?trace anch:isGeneratedByLearner ?learner ;
                   anch:tracesCompetency ?comp ;
                   anch:competencyScore ?score ;
                   anch:recordedAt ?timestamp ;
                   anch:derivedFromEvent ?event .
            ?comp a ?compClass .
            OPTIONAL { ?event proc:utteranceText ?utterance }
            BIND(REPLACE(STR(?compClass), ".*#", "") AS ?competency)
            BIND(COALESCE(REPLACE(STR(?event), ".*#", ""), "?") AS ?eventType)
        }
        ORDER BY ?timestamp
    """, initNs=NS)

    results["CQ2_alice_lineage"] = []
    for row in cq2:
        results["CQ2_alice_lineage"].append({
            "competency": str(row.competency),
            "score": float(row.score),
            "timestamp": str(row.timestamp),
            "event": str(row.eventType),
            "utterance": str(row.utterance)[:60] if row.utterance else "-",
        })

    # ═════════════════════════════════════════════════════════════════
    # CQ3: Interdisciplinary Bridges
    # "List all interdisciplinary bridges found in the project,
    #  their type, the domains they connect, and concepts involved."
    # ═════════════════════════════════════════════════════════════════
    cq3 = g.query("""
        SELECT ?bridgeName ?bridgeType ?domain1 ?domain2 ?concept1 ?concept2
        WHERE {
            ?bridge a ?bridgeClass ;
                    core:hasTitle ?bridgeName ;
                    know:bridgesDomain ?d1 ;
                    know:bridgesDomain ?d2 ;
                    know:linksConcept ?c1 ;
                    know:linksConcept ?c2 .
            ?d1 core:hasTitle ?domain1 .
            ?d2 core:hasTitle ?domain2 .
            ?c1 core:hasTitle ?concept1 .
            ?c2 core:hasTitle ?concept2 .
            FILTER(?d1 != ?d2)
            BIND(REPLACE(STR(?bridgeClass), ".*#", "") AS ?bridgeType)
        }
    """, initNs=NS)

    results["CQ3_bridges"] = []
    for row in cq3:
        results["CQ3_bridges"].append({
            "bridge": str(row.bridgeName),
            "type": str(row.bridgeType),
            "domain1": str(row.domain1),
            "domain2": str(row.domain2),
            "concept1": str(row.concept1),
            "concept2": str(row.concept2),
        })

    # ═════════════════════════════════════════════════════════════════
    # CQ4: Agent Trigger Summary
    # "Show which virtual agents were triggered by which discourse
    #  action types, and for which team."
    # ═════════════════════════════════════════════════════════════════
    cq4 = g.query("""
        SELECT ?agentType ?actionType ?teamName ?utterance
        WHERE {
            ?da a ?actionClass ;
                anch:triggersAgent ?agent ;
                proc:occursInPhase ?phase .
            ?agent a ?agentClass .
            ?agent team:monitorsTeam ?team .
            ?team core:hasTitle ?teamName .
            OPTIONAL { ?da proc:utteranceText ?utterance }
            BIND(REPLACE(STR(?agentClass), ".*#", "") AS ?agentType)
            BIND(REPLACE(STR(?actionClass), ".*#", "") AS ?actionType)
        }
    """, initNs=NS)

    results["CQ4_agent_triggers"] = []
    for row in cq4:
        results["CQ4_agent_triggers"].append({
            "agent": str(row.agentType),
            "action": str(row.actionType),
            "team": str(row.teamName),
            "utterance": str(row.utterance)[:60] if row.utterance else "-",
        })

    # CQ5: S2D cognitive pathway (Informed Design) — hypothesis → evidence →
    # principle → justified design activity, chained via transitive
    # isFollowedByAction and closed by informsDesign.
    cq5 = g.query("""
        SELECT ?hypothesis ?evidence ?principle ?designActivity ?conceptTitle
        WHERE {
            ?da_hyp a proc:HypothesisProposing ;
                    proc:timestamp ?t_hyp ;
                    proc:utteranceText ?hypothesis .
            ?da_hyp proc:isFollowedByAction* ?da_evid .
            ?da_evid a proc:EvidenceAnalyzing ;
                     proc:utteranceText ?evidence .
            ?da_evid proc:isFollowedByAction* ?da_princ .
            ?da_princ a proc:PrincipleFormulating ;
                      proc:utteranceText ?principle .
            ?da_princ proc:informsDesign ?activity .
            ?activity core:hasTitle ?designActivity .
            OPTIONAL {
                ?da_princ proc:referencesConcept ?concept .
                ?concept core:hasTitle ?conceptTitle
            }
        }
        ORDER BY ?t_hyp
    """, initNs=NS)

    results["CQ5_s2d_pathway"] = []
    for row in cq5:
        results["CQ5_s2d_pathway"].append({
            "hypothesis": str(row.hypothesis)[:60],
            "evidence": str(row.evidence)[:60],
            "principle": str(row.principle)[:60],
            "informs": str(row.designActivity),
            "concept": str(row.conceptTitle),
        })

    return results


def export_sparql_queries():
    """Export the 5 SPARQL queries as .sparql files."""
    QUERIES_DIR.mkdir(parents=True, exist_ok=True)

    queries = {
        "cq1_discourse_timeline.sparql": """
# CQ1: Discourse Timeline for a Given Phase
# Retrieve all discourse actions in the Create phase, ordered by timestamp,
# showing learner, action type, agent triggered, and referenced concept.

PREFIX core: <https://w3id.org/ie-pbl/ontology/1.0/module-core.ttl#>
PREFIX proc: <https://w3id.org/ie-pbl/ontology/1.0/module-process.ttl#>
PREFIX team: <https://w3id.org/ie-pbl/ontology/1.0/module-team.ttl#>
PREFIX anch: <https://w3id.org/ie-pbl/ontology/1.0/module-anchor.ttl#>

SELECT ?timestamp ?learnerName ?actionType ?utterance ?agentType
WHERE {
    ?phase a core:Create .
    ?da proc:occursInPhase ?phase ;
        proc:timestamp ?timestamp ;
        proc:isAttributedTo ?learner ;
        a ?actionTypeClass .
    ?learner team:hasName ?learnerName .
    OPTIONAL { ?da proc:utteranceText ?utterance }
    OPTIONAL { ?da anch:triggersAgent ?agent . ?agent a ?agentClass }
    BIND(REPLACE(STR(?actionTypeClass), ".*#", "") AS ?actionType)
    BIND(COALESCE(REPLACE(STR(?agentClass), ".*#", ""), "-") AS ?agentType)
}
ORDER BY ?timestamp
""",

        "cq2_performance_lineage.sparql": """
# CQ2: Complete Performance Lineage for a Learner
# Show all traces with competency, score, and originating event for learner "Alice".

PREFIX core: <https://w3id.org/ie-pbl/ontology/1.0/module-core.ttl#>
PREFIX proc: <https://w3id.org/ie-pbl/ontology/1.0/module-process.ttl#>
PREFIX team: <https://w3id.org/ie-pbl/ontology/1.0/module-team.ttl#>
PREFIX anch: <https://w3id.org/ie-pbl/ontology/1.0/module-anchor.ttl#>

SELECT ?competency ?score ?timestamp ?utterance
WHERE {
    ?learner team:hasName "Alice" .
    ?trace anch:isGeneratedByLearner ?learner ;
           anch:tracesCompetency ?comp ;
           anch:competencyScore ?score ;
           anch:recordedAt ?timestamp ;
           anch:derivedFromEvent ?event .
    ?comp a ?compClass .
    OPTIONAL { ?event proc:utteranceText ?utterance }
    BIND(REPLACE(STR(?compClass), ".*#", "") AS ?competency)
}
ORDER BY ?timestamp
""",

        "cq3_interdisciplinary_bridges.sparql": """
# CQ3: Interdisciplinary Bridges Detected
# List bridges, their type, the domains and concepts they connect.

PREFIX core: <https://w3id.org/ie-pbl/ontology/1.0/module-core.ttl#>
PREFIX know: <https://w3id.org/ie-pbl/ontology/1.0/module-knowledge.ttl#>

SELECT ?bridgeName ?bridgeType ?domain1 ?domain2 ?concept1 ?concept2
WHERE {
    ?bridge a ?bridgeClass ;
            core:hasTitle ?bridgeName ;
            know:bridgesDomain ?d1 ;
            know:bridgesDomain ?d2 ;
            know:linksConcept ?c1 ;
            know:linksConcept ?c2 .
    ?d1 core:hasTitle ?domain1 .
    ?d2 core:hasTitle ?domain2 .
    ?c1 core:hasTitle ?concept1 .
    ?c2 core:hasTitle ?concept2 .
    FILTER(?d1 != ?d2)
    BIND(REPLACE(STR(?bridgeClass), ".*#", "") AS ?bridgeType)
}
""",

        "cq4_agent_trigger_summary.sparql": """
# CQ4: Agent Trigger Summary
# Which agents were triggered by which discourse action types, and for which team?

PREFIX core: <https://w3id.org/ie-pbl/ontology/1.0/module-core.ttl#>
PREFIX proc: <https://w3id.org/ie-pbl/ontology/1.0/module-process.ttl#>
PREFIX team: <https://w3id.org/ie-pbl/ontology/1.0/module-team.ttl#>
PREFIX anch: <https://w3id.org/ie-pbl/ontology/1.0/module-anchor.ttl#>

SELECT ?agentType ?actionType ?teamName ?utterance
WHERE {
    ?da a ?actionClass ;
        anch:triggersAgent ?agent .
    ?agent a ?agentClass ;
           team:monitorsTeam ?team .
    ?team core:hasTitle ?teamName .
    OPTIONAL { ?da proc:utteranceText ?utterance }
    BIND(REPLACE(STR(?agentClass), ".*#", "") AS ?agentType)
    BIND(REPLACE(STR(?actionClass), ".*#", "") AS ?actionType)
}
""",
    "cq5_s2d_cognitive_pathway.sparql": """
# CQ5: S2D Cognitive Pathway (Informed Design)
# Traces a student's cognitive trajectory from HypothesisProposing through
# EvidenceAnalyzing to PrincipleFormulating, then via informsDesign to the
# engineering activity that the science informed. Uses transitive
# isFollowedByAction to chain discourse events.

PREFIX core: <https://w3id.org/ie-pbl/ontology/1.0/module-core.ttl#>
PREFIX proc: <https://w3id.org/ie-pbl/ontology/1.0/module-process.ttl#>

SELECT ?hypothesis ?evidence ?principle ?designActivity ?conceptTitle
WHERE {
    ?da_hyp a proc:HypothesisProposing ;
            proc:timestamp ?t_hyp ;
            proc:utteranceText ?hypothesis .
    ?da_hyp proc:isFollowedByAction* ?da_evid .
    ?da_evid a proc:EvidenceAnalyzing ;
             proc:utteranceText ?evidence .
    ?da_evid proc:isFollowedByAction* ?da_princ .
    ?da_princ a proc:PrincipleFormulating ;
              proc:utteranceText ?principle .
    ?da_princ proc:informsDesign ?activity .
    ?activity core:hasTitle ?designActivity .
    OPTIONAL {
        ?da_princ proc:referencesConcept ?concept .
        ?concept core:hasTitle ?conceptTitle
    }
}
ORDER BY ?t_hyp
""",
    }

    for fname, content in queries.items():
        path = QUERIES_DIR / fname
        path.write_text(content.strip())
        print(f"  ✓ {fname}")

    return QUERIES_DIR


def main():
    print("=" * 60)
    print("SPARQL Competency Questions: IE-PBL Ontology")
    print("=" * 60)

    # 1. Build TBox + ABox
    C = build_all_tbox()
    abox = build_vignette(C)
    print(f"\n  TBox + ABox: {len(list(default_world.individuals()))} individuals")

    # 2. Run SWRL rules via Pellet (real inference — v2.0)
    from build_swrl import build_swrl_rules, verify_swrl_inferences
    rules = build_swrl_rules(C)
    swrl_results = verify_swrl_inferences(C, rules)
    print(f"  ✓ SWRL: {len(swrl_results.get('orchestration',[]))} orchestration + {len(swrl_results.get('assessment',[]))} assessment inferences")

    # 3. Run SPARQL CQs
    print("\nExecuting SPARQL Competency Questions...")
    results = run_sparql_cqs()

    # 4. Report
    print("\n" + "=" * 60)
    print("COMPETENCY QUESTION RESULTS")
    print("=" * 60)

    cq_names = {
        "CQ1_discourse_timeline": "Discourse Timeline (Create phase)",
        "CQ2_alice_lineage": "Performance Lineage (Alice)",
        "CQ3_bridges": "Interdisciplinary Bridges",
        "CQ4_agent_triggers": "Agent Trigger Summary",
        "CQ5_s2d_pathway": "S2D Cognitive Pathway (CQ5, Informed Design)",
    }

    for key, label in cq_names.items():
        items = results.get(key, [])
        print(f"\n{'─' * 40}")
        print(f"{label}: {len(items)} results")
        print(f"{'─' * 40}")
        for item in items:
            print(f"  {json.dumps(item, ensure_ascii=False)}")

    # 5. Export .sparql files
    print(f"\nExporting SPARQL query files...")
    export_sparql_queries()

    print("\n✅ SPARQL CQ verification complete")
    return results


if __name__ == "__main__":
    main()
