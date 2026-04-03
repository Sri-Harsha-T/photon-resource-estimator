

GBS_OVERHEAD = {
    "squeezer_per_squeezing_op": 1,
    "beamsplitters_per_op": 1,
    "detector_per_mode" : 1,
    "ancilla_ratio" : 0.2, # 20% extra modes for error/routing
    "loss_overhead_factor" : 1.25, #25% overhead to account for optical loss
    "squeezing_db_default": 15, # realistic squeezing level in dB for overhead estimation
}

CLUSTER_STATE_OVERHEAD = {
    "squeezer_per_squeezing_op": 1.5, # more squeezing needed for cluster state generation
    "beamsplitters_per_op": 2, #network of beamsplitters for entanglement
    "detector_per_mode" : 1,
    "ancilla_ratio" : 0.5, # 50% extra modes for error/routing
    "loss_overhead_factor" : 1.5, #50% overhead to account for optical loss
    "squeezing_db_default": 12, # realistic squeezing level in dB for overhead estimation
}

BACKENDS = {
    "gbs": GBS_OVERHEAD,
    "cluster_state": CLUSTER_STATE_OVERHEAD,
}
