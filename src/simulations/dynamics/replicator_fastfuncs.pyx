import numpy as np
cimport numpy as np

DTYPE = np.float64
ctypedef np.float64_t DTYPE_t

DTYPE2 = np.int
ctypedef np.int_t DTYPE2_t


def generate_profiles(np.ndarray[DTYPE2_t] types, np.ndarray[DTYPE2_t, ndim=2] out=None):
    cdef int n = types.prod()
    cdef int plength = types.shape[0]
    cdef int m = n / types[0]
    cdef int j

    if out is None:
        out = np.zeros((n, plength), dtype=DTYPE2)

    out[:,0] = np.repeat(np.arange(types[0]), m)
    if types[1:].size:
        generate_profiles(types[1:], out=out[0:m,1:])
        for j in xrange(1, types[0]):
            out[j * m:(j + 1) * m, 1:] = out[0:m,1:]
    return out


def one_dimensional_step(np.ndarray[DTYPE_t, ndim=1] pop,
                         np.ndarray[DTYPE2_t, ndim=2] profiles,
                         np.ndarray[DTYPE_t, ndim=2] profile_payoffs,
                         DTYPE2_t types,
                         DTYPE2_t arity,
                         DTYPE_t background_rate):

    cdef np.ndarray[DTYPE2_t] profile
    cdef int i, j
    cdef int num_profiles = profiles.shape[0]
    cdef int profile_size = profiles[0].shape[0]
    cdef float zero = 0.
    cdef DTYPE_t profile_prob, avg_payoff
    cdef np.ndarray[DTYPE_t] newpop, expected_contribution, profile_probs
    cdef np.ndarray[DTYPE_t] payoffs = np.zeros(types, dtype=DTYPE)

    #go over each possible profile of strategies
    #for i in xrange(num_profiles)
    for i from 0 <= i < num_profiles:
        profile = profiles[i]
        profile_prob = 1.
        profile_probs = np.zeros(profile_size, dtype=DTYPE)

        #calculate the probability of that profile being drawn
        #for j in xrange(profile.shape[0]):
        for j from 0 <= j < profile_size:
            profile_probs[j] = pop[profile[j]]
        profile_prob = profile_probs.prod()

        #calculate the expected contribution for each of the profile slots
        if profile_prob > zero:
            expected_contribution = (profile_payoffs[i] / profile_probs) * profile_prob
        else:
            expected_contribution = profile_payoffs[i] * zero

        #add the expected contributions to the right type's payoff.
        #for j in xrange(profile.shape[0]):
        for j from 0 <= j < profile_size:
            payoffs[profile[j]] = payoffs[profile[j]] + expected_contribution[j]

    payoffs = payoffs / np.float64(arity)

    avg_payoff = np.dot(pop, payoffs)

    newpop = pop * (background_rate + payoffs) / (background_rate + avg_payoff)

    return newpop


def n_dimensional_step(np.ndarray[DTYPE_t, ndim=1] pop,
                       np.ndarray[DTYPE2_t, ndim=2] profiles,
                       np.ndarray[DTYPE_t, ndim=2] profile_payoffs,
                       np.ndarray[DTYPE2_t, ndim=1] types,
                       DTYPE_t background_rate):

    cdef int n = types.max()
    cdef np.ndarray[DTYPE2_t] profile
    cdef int i, j
    cdef int num_profiles = profiles.shape[0]
    cdef int profile_size = profiles[0].shape[0]
    cdef int num_pops = types.shape[0]
    cdef float zero = 0.
    cdef DTYPE_t profile_prob
    cdef np.ndarray[DTYPE_t, ndim=2] newpop
    cdef np.ndarray[DTYPE_t] expected_contribution, profile_probs, avg_payoffs
    cdef np.ndarray[DTYPE_t, ndim=2] payoffs = np.zeros((num_pops, types.max()), dtype=DTYPE)

    #go over each possible profile of strategies
    #for i in xrange(profiles.shape[0]):
    for i from 0 <= i < num_profiles:
        profile = profiles[i]
        profile_prob = 1.
        profile_probs = np.zeros(profile_size, dtype=DTYPE)

        #calculate the probability of that profile being drawn
        #for j in xrange(profile.shape[0]):
        for j from 0 <= j < profile_size:
            profile_probs[j] = pop[j * n + profile[j]]
        profile_prob = profile_probs.prod()

        #calculate the expected contribution for each of the profile slots
        if profile_prob > zero:
            expected_contribution = (profile_payoffs[i] / profile_probs) * profile_prob
        else:
            expected_contribution = profile_payoffs[i] * zero

        #add the expected contributions to the right type's payoff.
        #for j in xrange(profile.shape[0]):
        for j from 0 <= j < profile_size:
            payoffs[j][profile[j]] = payoffs[j][profile[j]] + expected_contribution[j]

    avg_payoffs = np.ones(num_pops, dtype=DTYPE)
    newpop = np.zeros([num_pops, types.max()], dtype=DTYPE)
    #for i in xrange(types.shape[0]):
    for i from 0 <= i < num_pops:
        avg_payoffs[i] = np.dot(pop[(i * n):((i + 1) * n)], payoffs[i])
        newpop[i] = pop[(i * n):((i + 1) * n)] * (background_rate + payoffs[i]) / (background_rate + avg_payoffs[i])

    return newpop

