import functools


class TableDecorators:
    @classmethod
    def dissort(cls, table_lambda=lambda self: self, resume_sortable: bool = True):
        """

        :param table_lambda: lambda, input 'self', output table
        :param resume_sortable: if True, after func executed, the sortingEnabled property will be reset to True.
        :return:
        """

        def inner(func):
            @functools.wraps(func)
            def func_wrapper(*args, **kwargs):
                # args[0] is 'self'
                table = table_lambda(args[0])
                table.setSortingEnabled(False)
                result = func(*args, **kwargs)
                # In a multi-threaded environment, it can not be resume to old state.
                if resume_sortable:
                    table.setSortingEnabled(True)
                return result

            return func_wrapper

        return inner

    @classmethod
    def blockSignals(cls, func):
        def func_wrapper(*args, **kwargs):
            table = args[0]
            table.blockSignals(True)
            result = func(*args, **kwargs)
            table.blockSignals(False)
            return result

        return func_wrapper


def clearLayout(layout):
    while layout.count():
        child = layout.takeAt(0)
        if child.widget() is not None:
            child.widget().setParent(None)
        elif child.layout() is not None:
            clearLayout(child.layout())
