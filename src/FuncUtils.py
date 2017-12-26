from functools import partial


def MakeFunc(func, callback):
    def Run(func, callback):
        callback(func())
    return partial(Run, func, callback)


async def AsyncRunAll(loop, funcs):
    futures = []
    for fn in funcs:
        futures.append(loop.run_in_executor(None, fn))
    for f in futures:
        await f
    return
