def onScale(scale, arg):
    """
        return nextInterval in sec
    """
    t = "default" if "type" not in scale else scale["type"]

    lastInterval, idx = arg

    if t == "generative":
        if idx == 0:
            return scale["firstVal"]
        else:
            func = eval(scale["func"])
            return func(arg)
    elif t == "default":
        intervals = scale["intervals"]

        nextInterval = intervals[idx] if idx<len(intervals) else intervals[-1]
        return nextInterval

def scaleMemDoneCount(scale):
    """
        return nextInterval in sec
    """
    t = "default" if "type" not in scale else scale["type"]

    doneCount = 21
    if t == "generative":
        if "doneCount" in scale:
            doneCount = 21
    elif t == "default":
        doneCount = len(scale["intervals"])

    return doneCount
