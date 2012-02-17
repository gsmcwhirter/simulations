import numpy as np
cimport numpy as np
cimport cython

DTYPE = np.float64
ctypedef np.float64_t DTYPE_t

DTYPE2 = np.int
ctypedef np.int_t DTYPE2_t

np.import_array()


@cython.boundscheck(False)
def generate_profiles(np.ndarray[DTYPE2_t] types not None,
                      np.ndarray[DTYPE2_t, ndim=2] out=None):
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


@cython.boundscheck(False)
def pop_equals(np.ndarray newpop not None,
               np.ndarray prevpop not None,
               DTYPE_t effective_zero):
    if newpop.ndim == 1:
        return one_pop_equals(newpop, prevpop, effective_zero)
    elif newpop.ndim == 2:
        return n_pop_equals(newpop, prevpop, effective_zero)
    else:
        raise ValueError("Can only handle 1 or 2 dimensions")


@cython.boundscheck(False)
cdef int n_pop_equals(np.ndarray[DTYPE_t, ndim=2] newpop,
                       np.ndarray[DTYPE_t, ndim=2] prevpop,
                       DTYPE_t effective_zero):
    cdef int one = 1
    cdef int n = newpop.shape[0]
    cdef DTYPE_t neg_effective_zero = -1 * effective_zero
    cdef int same
    for i from 0 <= i < n:
        same = one_pop_equals(newpop[i], prevpop[i], effective_zero)
        if same == 0:
            return 0

    return one


@cython.boundscheck(False)
cdef int one_pop_equals(np.ndarray[DTYPE_t, ndim=1] newpop,
                         np.ndarray[DTYPE_t, ndim=1] prevpop,
                         DTYPE_t effective_zero):

    cdef int one = 1
    cdef int n = newpop.shape[0]
    cdef DTYPE_t neg_effective_zero = -1 * effective_zero
    cdef DTYPE_t diff
    for i from 0 <= i < n:
        diff = (newpop[i] - prevpop[i])
        if diff < neg_effective_zero or diff > effective_zero:
            return 0

    return one


@cython.boundscheck(False)
cpdef np.ndarray[DTYPE_t, ndim=1] one_dimensional_step(np.ndarray[DTYPE_t, ndim=1] pop,
                                                       np.ndarray[DTYPE2_t, ndim=2] profiles,
                                                       np.ndarray[DTYPE2_t, ndim=1] sample_profile,
                                                       np.ndarray[DTYPE_t, ndim=2] profile_payoffs,
                                                       np.ndarray[DTYPE2_t, ndim=1] types_array,
                                                       np.ndarray[DTYPE2_t, ndim=1] types_array_2,
                                                       DTYPE2_t arity,
                                                       DTYPE_t background_rate,
                                                       DTYPE_t effective_zero,
                                                       DTYPE2_t num_profiles,
                                                       DTYPE2_t profile_size):

    cdef int i, j, strategy
    cdef int types = types_array.shape[0]
    cdef int izero = <int>0
    cdef int ione = <int>1
    cdef DTYPE_t profile_prob, avg_payoff, prob, contrib, contrib2, tmp = 0.
    cdef DTYPE_t arityf = <DTYPE_t>arity
    cdef DTYPE_t zero = 0.
    cdef np.ndarray[DTYPE_t, ndim=1] expected_contribution, profile_probs
    cdef np.npy_intp* dims = np.PyArray_DIMS(types_array)
    cdef np.npy_intp* new_dims = np.PyArray_DIMS(types_array_2)
    cdef np.npy_intp* profile_dims = np.PyArray_DIMS(sample_profile)
    cdef np.ndarray[DTYPE_t, ndim=1] newpop2 = np.PyArray_ZEROS(ione, dims, np.NPY_FLOAT64, izero)
    cdef np.ndarray[DTYPE_t, ndim=1] payoffs = np.PyArray_ZEROS(ione, dims, np.NPY_FLOAT64, izero)
    cdef np.ndarray[DTYPE_t, ndim=1] newpop = np.PyArray_ZEROS(ione, new_dims, np.NPY_FLOAT64, izero)

    #go over each possible profile of strategies
    for i from 0 <= i < num_profiles:
        profile_prob = 1.
        #profile_probs = np.empty(profile_size, dtype=DTYPE)
        profile_probs = np.PyArray_EMPTY(1, profile_dims, np.NPY_FLOAT64, 0)
        expected_contribution = np.PyArray_ZEROS(1, profile_dims, np.NPY_FLOAT64, 0)

        #calculate the probability of that profile being drawn
        #profile_prob = profile_probs.prod()
        for j from 0 <= j < profile_size:
            strategy = (<int*>np.PyArray_GETPTR2(profiles, i, j))[0]
            prob = (<DTYPE_t*>np.PyArray_GETPTR1(pop, strategy))[0]
            #np.PyArray_SETITEM(profile_probs, np.PyArray_GETPTR1(profile_probs, j), prob)
            profile_probs[j] = prob
            profile_prob = profile_prob * prob

        #calculate the expected contribution for each of the profile slots
        for j from 0 <= j < profile_size:
            if profile_prob > zero:
            #expected_contribution = (profile_payoffs[i] / profile_probs) * profile_prob
                contrib = (<DTYPE_t*>np.PyArray_GETPTR2(profile_payoffs, i, j))[0]
                prob = (<DTYPE_t*>np.PyArray_GETPTR1(profile_probs, j))[0]
                contrib = contrib * profile_prob / prob
                #np.PyArray_SETITEM(expected_contribution, np.PyArray_GETPTR1(expected_contribution, j), contrib)
                expected_contribution[j] = contrib
            else:
                #expected_contribution = profile_payoffs[i] * zero
                #np.PyArray_SETITEM(expected_contribution, np.PyArray_GETPTR1(expected_contribution, j), zero)
                expected_contribution[j] = zero

        #add the expected contributions to the right type's payoff.
        for j from 0 <= j < profile_size:
            #payoffs[profile[j]] = payoffs[profile[j]] + expected_contribution[j]
            strategy = (<int*>np.PyArray_GETPTR2(profiles, i, j))[0]
            contrib = (<DTYPE_t*>np.PyArray_GETPTR1(payoffs, strategy))[0]
            contrib2 = (<DTYPE_t*>np.PyArray_GETPTR1(expected_contribution, j))[0]
            #np.PyArray_SETITEM(payoffs, np.PyArray_GETPTR1(payoffs, strategy), contrib + contrib2)
            payoffs[strategy] = contrib + contrib2

    #payoffs = payoffs / <float>arity
    for i from 0 <= i < types:
        contrib = (<DTYPE_t*>np.PyArray_GETPTR1(payoffs, i))[0]
        contrib = contrib / arityf
        np.PyArray_SETITEM(payoffs, np.PyArray_GETPTR1(payoffs, i), contrib)

    #avg_payoff = np.dot(pop, payoffs)
    avg_payoff = <DTYPE_t>0
    for i from 0 <= i < types:
        contrib = (<DTYPE_t*>np.PyArray_GETPTR1(pop, i))[0]
        contrib2 = (<DTYPE_t*>np.PyArray_GETPTR1(payoffs, i))[0]
        avg_payoff = <DTYPE_t>(avg_payoff + (contrib * contrib2))

    #newpop = pop * (background_rate + payoffs) / (background_rate + avg_payoff)
    for i from 0 <= i < types:
        contrib = (<DTYPE_t*>np.PyArray_GETPTR1(pop, i))[0]
        contrib2 = (<DTYPE_t*>np.PyArray_GETPTR1(payoffs, i))[0]
        tmp = contrib * (background_rate + contrib2) / (background_rate + avg_payoff)
        #np.PyArray_SETITEM(newpop2, np.PyArray_GETPTR1(newpop2, i), tmp)
        #np.PyArray_SETITEM(newpop, np.PyArray_GETPTR1(newpop, <int>(i + 1)), tmp)
        newpop2[i] = tmp
        newpop[i + 1] = tmp

    #newpop = np.insert(newpop, 0, one_pop_equals(newpop, pop, effective_zero))
    np.PyArray_SETITEM(newpop, np.PyArray_GETPTR1(newpop, 0), <DTYPE_t>one_pop_equals(newpop2, pop, effective_zero))

    return newpop


@cython.boundscheck(False)
cpdef np.ndarray[DTYPE_t, ndim=2] n_dimensional_step(np.ndarray[DTYPE_t, ndim=2] pop,
                                                     np.ndarray[DTYPE2_t, ndim=2] profiles,
                                                     np.ndarray[DTYPE2_t, ndim=1] sample_profile,
                                                     np.ndarray[DTYPE_t, ndim=2] profile_payoffs,
                                                     np.ndarray[DTYPE2_t, ndim=2] types_array,
                                                     np.ndarray[DTYPE2_t, ndim=2] types_array_2,
                                                     DTYPE_t background_rate,
                                                     DTYPE_t effective_zero,
                                                     np.ndarray[DTYPE2_t, ndim=1] type_counts,
                                                     DTYPE2_t num_profiles,
                                                     DTYPE2_t profile_size):

    cdef int i, j, strategy
    cdef int izero = <int>0
    cdef int ione = <int>1
    cdef int itwo = <int>2
    cdef int num_pops = types_array.shape[0]
    cdef int types = types_array.shape[1]
    cdef DTYPE_t zero = 0.
    cdef DTYPE_t profile_prob, prob, contrib, contrib2, tmp = 0.
    cdef np.ndarray[DTYPE_t, ndim=1] expected_contribution, profile_probs
    cdef np.npy_intp* dims = np.PyArray_DIMS(types_array)
    cdef np.npy_intp* new_dims = np.PyArray_DIMS(types_array_2)
    cdef np.npy_intp* profile_dims = np.PyArray_DIMS(sample_profile)
    cdef np.npy_intp* by_pop_dims = np.PyArray_DIMS(type_counts)
    cdef np.ndarray[DTYPE_t, ndim=2] newpop2 = np.PyArray_ZEROS(itwo, dims, np.NPY_FLOAT64, izero)
    cdef np.ndarray[DTYPE_t, ndim=2] payoffs = np.PyArray_ZEROS(itwo, dims, np.NPY_FLOAT64, izero)
    cdef np.ndarray[DTYPE_t, ndim=2] newpop = np.PyArray_ZEROS(itwo, new_dims, np.NPY_FLOAT64, izero)
    cdef np.ndarray[DTYPE_t, ndim=1] avg_payoffs = np.PyArray_ZEROS(ione, by_pop_dims, np.NPY_FLOAT64, izero)

    #go over each possible profile of strategies
    for i from 0 <= i < num_profiles:
        profile_prob = 1.
        profile_probs = np.PyArray_EMPTY(1, profile_dims, np.NPY_FLOAT64, 0)
        expected_contribution = np.PyArray_ZEROS(1, profile_dims, np.NPY_FLOAT64, 0)

        #calculate the probability of that profile being drawn
        for j from 0 <= j < profile_size:
            #profile_probs[j] = pop[j][profile[j]]
            #profile_prob = profile_prob * pop[j][profile[j]]
            strategy = (<int*>np.PyArray_GETPTR2(profiles, i, j))[0]
            prob = (<DTYPE_t*>np.PyArray_GETPTR2(pop, j, strategy))[0]
            #np.PyArray_SETITEM(profile_probs, np.PyArray_GETPTR1(profile_probs, j), prob)
            profile_probs[j] = prob
            profile_prob = profile_prob * prob
        #profile_prob = profile_probs.prod()

        #calculate the expected contribution for each of the profile slots
        #if profile_prob > zero:
        #    expected_contribution = (profile_payoffs[i] / profile_probs) * profile_prob
        #else:
        #    expected_contribution = profile_payoffs[i] * zero
        #calculate the expected contribution for each of the profile slots
        for j from 0 <= j < profile_size:
            if profile_prob > zero:
            #expected_contribution = (profile_payoffs[i] / profile_probs) * profile_prob
                contrib = (<DTYPE_t*>np.PyArray_GETPTR2(profile_payoffs, i, j))[0]
                prob = (<DTYPE_t*>np.PyArray_GETPTR1(profile_probs, j))[0]
                contrib = contrib * profile_prob / prob
                #np.PyArray_SETITEM(expected_contribution, np.PyArray_GETPTR1(expected_contribution, j), contrib)
                expected_contribution[j] = contrib
            else:
                #expected_contribution = profile_payoffs[i] * zero
                #np.PyArray_SETITEM(expected_contribution, np.PyArray_GETPTR1(expected_contribution, j), zero)
                expected_contribution[j] = zero

        #add the expected contributions to the right type's payoff.
        #for j from 0 <= j < profile_size:
        #    payoffs[j][profile[j]] = payoffs[j][profile[j]] + expected_contribution[j]
        for j from 0 <= j < profile_size:
            #payoffs[profile[j]] = payoffs[profile[j]] + expected_contribution[j]
            strategy = (<int*>np.PyArray_GETPTR2(profiles, i, j))[0]
            contrib = (<DTYPE_t*>np.PyArray_GETPTR2(payoffs, j, strategy))[0]
            contrib2 = (<DTYPE_t*>np.PyArray_GETPTR1(expected_contribution, j))[0]
            np.PyArray_SETITEM(payoffs, np.PyArray_GETPTR2(payoffs, j, strategy), contrib + contrib2)


    for i from 0 <= i < num_pops:
        for j from 0 <= j < types:
            contrib = (<DTYPE_t*>np.PyArray_GETPTR2(pop, i, j))[0]
            contrib2 = (<DTYPE_t*>np.PyArray_GETPTR2(payoffs, i, j))[0]
            avg_payoffs[i] = avg_payoffs[i] + (contrib * contrib2)

        for j from 0 <= j < types:
            contrib = (<DTYPE_t*>np.PyArray_GETPTR2(pop, i, j))[0]
            contrib2 = (<DTYPE_t*>np.PyArray_GETPTR2(payoffs, i, j))[0]
            tmp = (contrib * (background_rate + contrib2) / (background_rate + avg_payoffs[i]))
            np.PyArray_SETITEM(newpop2, np.PyArray_GETPTR2(newpop2, i, j), tmp)
            np.PyArray_SETITEM(newpop, np.PyArray_GETPTR2(newpop, <int>(i + 1), j), tmp)

    tmp = <DTYPE_t>n_pop_equals(newpop2, pop, effective_zero)
    for j from 0 <= j < types:
        np.PyArray_SETITEM(newpop, np.PyArray_GETPTR2(newpop, 0, j), tmp)

    return newpop

