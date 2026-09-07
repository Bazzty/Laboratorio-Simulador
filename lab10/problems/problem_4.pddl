(define (problem problem_4)
  (:domain manito)

  (:objects
    A R G B - item
    zona-a zona-r zona-g zona-b zona-derecha zona-izquierda - zone
  )

  (:init
    (at A zona-derecha)
    (at B zona-izquierda)
    (at G zona-g)
    (at R zona-b)
    (clean zona-a)
    (clean zona-r)
    (clear A)
    (clear B)
    (clear G)
    (clear R)
    (hand-empty)
    (stackable A)
    (stackable R)
    (stackable G)
    (stackable B)
  )

  (:goal
    (on G B)
  )
)
