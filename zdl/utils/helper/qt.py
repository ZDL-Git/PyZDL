import functools


class TableDecorators:
    @classmethod
    def dissort(cls, table_lambda=lambda self: self, reset: bool = True):
        """

        :param table_lambda: lambda, input 'self', output table
        :param reset: if True, after func executed, the sortingEnabled property will be reset to old state.
        :return:
        """

        def inner(func):
            @functools.wraps(func)
            def func_wrapper(*args, **kwargs):
                # args[0] is 'self' arg
                table = table_lambda(args[0])
                old_state = table.isSortingEnabled()
                table.setSortingEnabled(False)
                result = func(*args, **kwargs)
                if reset:
                    table.setSortingEnabled(old_state)
                return result

            return func_wrapper

        return inner

    @classmethod
    def block_signals(cls, func):
        def func_wrapper(*args, **kwargs):
            table = args[0]
            table.blockSignals(True)
            result = func(*args, **kwargs)
            table.blockSignals(False)
            return result

        return func_wrapper


def clear_layout(layout):
    while layout.count():
        child = layout.takeAt(0)
        if child.widget() is not None:
            child.widget().setParent(None)
        elif child.layout() is not None:
            clear_layout(child.layout())
