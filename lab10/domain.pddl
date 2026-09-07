(define (domain manito)

    (:requirements :strips :typing)

    (:types
      ; TODO: los definimos juntos
      item ; algo que el brazo puede tomar
      zone ; zona donde se encuentra un item
    )
    
    (:predicates
    (at ?o - item ?z - zone ) ; el item ?o está en la zona ?z
    (clean ?z - zone) ; la zona ?z está libre, no tiene nada encima
    (clear ?o - item) ; el item ?o no tiene nada apilado encima
    (hand-empty) ; el gripper del brazo está vacío
    (hand-pick ?o - item) ; el brazo está sujetando el item ?o
    (on ?o - item ?p - item) ; el item ?o está apilado sobre el item ?p
    (stackable ?o - item) ; el item ?o admite que se apile algo sobre él
    )

    ; --- acciones ---

    (:action pick-up
      ; agarrar un item ?o que está suelto sobre la zona ?z
      :parameters (?o - item ?z - zone)
      :precondition (and (at ?o ?z) (clear ?o) (hand-empty))
      :effect (and
        (not (at ?o ?z))
        (not (hand-empty))
        (hand-pick ?o)
        (clean ?z)
      )
    )

    (:action put-down
      ; soltar el item que se tiene en la mano sobre una zona libre ?z
      :parameters (?o - item ?z - zone)
      :precondition (and (hand-pick ?o) (clean ?z))
      :effect (and
        (not (hand-pick ?o))
        (hand-empty)
        (at ?o ?z)
        (not (clean ?z))
        (clear ?o)
      )
    )

    (:action stack
      ; apilar el item que se tiene en la mano ?o sobre otro item ?p
      :parameters (?o - item ?p - item)
      :precondition (and (hand-pick ?o) (clear ?p) (stackable ?p))
      :effect (and
        (not (hand-pick ?o))
        (hand-empty)
        (on ?o ?p)
        (not (clear ?p))
        (clear ?o)
      )
    )

    (:action unstack
      ; agarrar el item ?o que está apilado encima de ?p
      :parameters (?o - item ?p - item)
      :precondition (and (on ?o ?p) (clear ?o) (hand-empty))
      :effect (and
        (not (on ?o ?p))
        (clear ?p)
        (not (hand-empty))
        (hand-pick ?o)
      )
    )

  )
