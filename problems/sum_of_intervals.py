from functools import partial, reduce


def sum_of_intervals(intervals):
    mergedIntervals = set()
    for interval in intervals:
        mergedIntervals = _process_interval_for(mergedIntervals, interval)
    return sum(interval[1] - interval[0] for interval in mergedIntervals)


def _process_interval_for(mergedIntervals, intervalToAdd):
    intervals = set(
        filter(partial(_interval_overlaps, intervalToAdd), mergedIntervals))
    intervals.add(intervalToAdd)
    mergedIntervals -= intervals
    mergedIntervals.add(_merge_intervals(intervals))
    return mergedIntervals


def _interval_overlaps(x, y):
    return x[0] <= y[1] and y[0] <= x[1]


def _merge_intervals(intervals):
    return reduce(lambda x, y: (min(x[0], y[0]), max(x[1], y[1])), intervals)
