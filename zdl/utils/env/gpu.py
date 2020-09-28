from zdl.utils.env.terminal import Terminal


class GPU(Terminal):

    @classmethod
    def supported(cls):
        try:
            if int(cls.checkOutput('nvidia-smi > /dev/null '
                                   '&& nvidia-smi --query-gpu=name --format=csv,noheader | wc -l')) > 0:
                return True
            return False
        except Exception:
            return False

    @classmethod
    def cards(cls):
        try:
            return cls.checkOutput('nvidia-smi --query-gpu=name --format=csv,noheader')
        except Exception:
            return None
