#!/usr/bin/env python3
"""
owl_helpers.py — Factory functions for building OWL 2 DL ontology elements.

Replaces the repetitive pattern of manually creating symmetric property pairs,
datatype properties, covering axioms, and disjointness declarations.

Usage:
    from owl_helpers import make_property_pair, make_datatype_prop, declare_covering

    with onto:
        hasX, isXOf = make_property_pair(onto, "hasX", "isXOf", A, B)
        startTime = make_datatype_prop(onto, "startTime", [Project, Phase], datetime)
        declare_covering(Phase, [Ask, Imagine, Plan, Create, Improve])
"""

from owlready2 import (
    Thing, ObjectProperty, DatatypeProperty, TransitiveProperty,
    SymmetricProperty, FunctionalProperty,
    AllDisjoint, Or, ThingClass
)


# ──────────────────────────────────────────────────────────────────────────────
# Class Factory
# ──────────────────────────────────────────────────────────────────────────────

def make_class(onto, name, bases=(Thing,), label=None, comment=None):
    """
    Create an OWL class with optional label and comment.

    Args:
        onto: owlready2 Ontology to attach the class to
        name: class name (string)
        bases: tuple of superclasses (default: (Thing,))
        label: rdfs:label string (without @en suffix)
        comment: rdfs:comment string (without @en suffix)

    Returns:
        The created ThingClass
    """
    cls = type(name, bases, {"namespace": onto})
    if label:
        cls.label.append(f"{label}@en")
    if comment:
        cls.comment.append(f"{comment}@en")
    return cls


# ──────────────────────────────────────────────────────────────────────────────
# Property Factories
# ──────────────────────────────────────────────────────────────────────────────

def make_property_pair(onto, name_fwd, name_rev, domain, range_,
                       transitive=False, symmetric=False, functional=False):
    """
    Create a forward/reverse object property pair with correct inverse linkage.

    Example:
        hasPhase, isPhaseOf = make_property_pair(onto, "hasPhase", "isPhaseOf",
                                                  Project, Phase)

    Args:
        onto: owlready2 Ontology
        name_fwd: forward property name (e.g. "hasPhase")
        name_rev: reverse property name (e.g. "isPhaseOf")
        domain: domain class or list of classes
        range_: range class or list of classes
        transitive: if True, both properties are TransitiveProperty
        symmetric: if True, the forward property is SymmetricProperty
        functional: if True, the forward property is FunctionalProperty

    Returns:
        (forward_property, reverse_property) tuple
    """
    # Build base classes for forward property
    fwd_bases = [ObjectProperty]
    if transitive:
        fwd_bases.insert(0, TransitiveProperty)
    if symmetric:
        fwd_bases.insert(0, SymmetricProperty)
    if functional:
        fwd_bases.insert(0, FunctionalProperty)
    fwd_bases = tuple(fwd_bases)

    rev_bases = [ObjectProperty]
    if transitive:
        rev_bases.insert(0, TransitiveProperty)
    rev_bases = tuple(rev_bases)

    # Create forward property
    prop_fwd = type(name_fwd, fwd_bases, {"namespace": onto})
    prop_fwd.label.append(f"{name_fwd}@en")

    # Create reverse property
    prop_rev = type(name_rev, rev_bases, {"namespace": onto})
    prop_rev.label.append(f"{name_rev}@en")

    # Set domain/range
    _set_domain(prop_fwd, domain)
    _set_range(prop_fwd, range_)
    _set_domain(prop_rev, range_)
    _set_range(prop_rev, domain)

    # Link inverses
    prop_fwd.inverse_property = prop_rev

    return prop_fwd, prop_rev


def make_datatype_prop(onto, name, domain, range_type):
    """
    Create a datatype property.

    Args:
        onto: owlready2 Ontology
        name: property name
        domain: class or Or() expression, or list
        range_type: Python type (str, int, float, datetime.datetime)

    Returns:
        The created DatatypeProperty
    """
    prop = type(name, (DatatypeProperty,), {"namespace": onto})
    prop.label.append(f"{name}@en")
    _set_domain(prop, domain)
    prop.range = [range_type]
    return prop


def _set_domain(prop, domain):
    """Set domain on a property, handling list/Or/single-class cases."""
    if isinstance(domain, list):
        prop.domain = domain
    else:
        prop.domain.append(domain)


def _set_range(prop, range_):
    """Set range on a property, handling list/Or/single-class cases."""
    if isinstance(range_, list):
        for r in range_:
            prop.range.append(r)
    else:
        prop.range.append(range_)


# ──────────────────────────────────────────────────────────────────────────────
# Axiom Helpers
# ──────────────────────────────────────────────────────────────────────────────

def declare_covering(named_class, subclasses):
    """
    Declare that named_class is exactly the union of its subclasses.

    Example:
        declare_covering(DiscourseAction,
                         [HelpSeeking, FailureReporting, PeerArgumentation])

    Args:
        named_class: the parent class
        subclasses: list of subclass ThingClass objects
    """
    or_expr = subclasses[0]
    for sc in subclasses[1:]:
        or_expr = or_expr | sc
    named_class.equivalent_to = [or_expr]


def declare_disjoint(*classes):
    """
    Declare AllDisjoint for a variable number of classes.

    Example:
        declare_disjoint(Project, Phase, Activity, Constraint, Deliverable)
    """
    AllDisjoint(list(classes))
