(define (problem problem_5)
  (:domain manito)

  (:objects
    A R G B - item
    zona-a zona-r zona-g zona-b zona-derecha zona-izquierda - zone
  )

  (:init
    (at A zona-derecha)
    (at B zona-izquierda)
    (at R zona-b)
    (on G B)
    (clean zona-a)
    (clean zona-r)
    (clean zona-g)
    (clear A)
    (clear G)
    (clear R)
    (hand-empty)
    (stackable A)
    (stackable R)
    (stackable G)
    (stackable B)
  )

  (:goal
    (on A R)
  )
)
