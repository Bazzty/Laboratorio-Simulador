(define (problem problem_9)
  (:domain manito)
  (:objects
    A R G B - item
    zona-a zona-r zona-g zona-b zona-derecha - zone
  )
  (:init
    (at A zona-a) (at R zona-r) (at G zona-g) (at B zona-b)
    (clean zona-derecha)
    (clear A) (clear R) (clear G) (clear B)
    (hand-empty)
    (stackable A) (stackable R) (stackable G) (stackable B)
  )
  (:goal
    (and (on A R) (on R G) (at G zona-derecha))
  )
)