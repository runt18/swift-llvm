class Command:
    def __init__(self, args, redirects):
        self.args = list(args)
        self.redirects = list(redirects)

    def __repr__(self):
        return 'Command({0!r}, {1!r})'.format(self.args, self.redirects)

    def __eq__(self, other):
        if not isinstance(other, Command):
            return False

        return ((self.args, self.redirects) ==
                (other.args, other.redirects))

    def toShell(self, file):
        for arg in self.args:
            if "'" not in arg:
                quoted = "'{0!s}'".format(arg)
            elif '"' not in arg and '$' not in arg:
                quoted = '"{0!s}"'.format(arg)
            else:
                raise NotImplementedError('Unable to quote {0!r}'.format(arg))
            file.write(quoted)

            # For debugging / validation.
            import ShUtil
            dequoted = list(ShUtil.ShLexer(quoted).lex())
            if dequoted != [arg]:
                raise NotImplementedError('Unable to quote {0!r}'.format(arg))

        for r in self.redirects:
            if len(r[0]) == 1:
                file.write("{0!s} '{1!s}'".format(r[0][0], r[1]))
            else:
                file.write("{0!s}{1!s} '{2!s}'".format(r[0][1], r[0][0], r[1]))

class Pipeline:
    def __init__(self, commands, negate=False, pipe_err=False):
        self.commands = commands
        self.negate = negate
        self.pipe_err = pipe_err

    def __repr__(self):
        return 'Pipeline({0!r}, {1!r}, {2!r})'.format(self.commands, self.negate,
                                         self.pipe_err)

    def __eq__(self, other):
        if not isinstance(other, Pipeline):
            return False

        return ((self.commands, self.negate, self.pipe_err) ==
                (other.commands, other.negate, self.pipe_err))

    def toShell(self, file, pipefail=False):
        if pipefail != self.pipe_err:
            raise ValueError('Inconsistent "pipefail" attribute!')
        if self.negate:
            file.write('! ')
        for cmd in self.commands:
            cmd.toShell(file)
            if cmd is not self.commands[-1]:
                file.write('|\n  ')

class Seq:
    def __init__(self, lhs, op, rhs):
        assert op in (';', '&', '||', '&&')
        self.op = op
        self.lhs = lhs
        self.rhs = rhs

    def __repr__(self):
        return 'Seq({0!r}, {1!r}, {2!r})'.format(self.lhs, self.op, self.rhs)

    def __eq__(self, other):
        if not isinstance(other, Seq):
            return False

        return ((self.lhs, self.op, self.rhs) ==
                (other.lhs, other.op, other.rhs))

    def toShell(self, file, pipefail=False):
        self.lhs.toShell(file, pipefail)
        file.write(' {0!s}\n'.format(self.op))
        self.rhs.toShell(file, pipefail)
