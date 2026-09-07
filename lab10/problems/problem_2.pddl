(define (problem problem_2)
  (:domain manito)

  (:objects
    A R G B - item
    zona-a zona-r zona-g zona-b zona-derecha zona-izquierda - zone
  )

  (:init
    (at A zona-derecha)
    (at R zona-r)
    (at G zona-g)
    (at B zona-b)
    (clean zona-a)
    (clean zona-izquierda)
    (clear A)
    (clear R)
    (clear G)
    (clear B)
    (hand-empty)
    (stackable A)
    (stackable R)
    (stackable G)
    (stackable B)
  )

  (:goal
    (at B zona-izquierda)
  )
)
