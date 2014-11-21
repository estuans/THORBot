from operator import itemgetter

from .base import BaseCommand

class SimpleCalculator(BaseCommand):

    help_message = "Performs simple calculations, supports addition, subtraction, division, multiplication and modulo. e.g. 128 * 10"
    listen = "calc"

    def perform_action(self):
        try:
            #import pdb; pdb.set_trace()
            arglist = self.message.split('alc ')

            calclist = arglist[1].split(" ")
            #Fetch arguments

            calc1 = itemgetter(0)(calclist)
            opera = itemgetter(1)(calclist)
            calc2 = itemgetter(2)(calclist)

        except IndexError:
            error = "ERROR: list index out of range"
            self.respond(error)
            return

        #Translate to int
        calc1 = int(calc1)
        calc2 = int(calc2)

        #Check if Operator is valid
        valid = ['+', '/', '-', '*', '%']


        if calc1 != int(calc1):
            msg = "ERROR: ARG1 INCORRECT"
            self.respond(msg)

        if opera not in valid:
            msg = "ERROR: OPERATOR INCORRECT"
            self.respond(msg)

        if calc2 != int(calc2):
            msg = "ERROR: ARG2 INCORRECT"
            self.respond(msg)

        #Use the very dangerous eval function
        result = eval("{0}{1}{2}".format(calc1,opera,calc2))
        reply = "%s %s %s = %s" % (calc1, opera, calc2, result)
        self.respond(reply)


class AdvancedCalculator(BaseCommand):

    help_message = "Performs simple calculations, supports addition, subtraction, division, multiplication and modulo. e.g. 128 * 10"
    listen = "sci"

    def perform_action(self):
        arglist = self.message.split('sci ')
        arg = arglist[1]

        from math import *

        #make a list of safe functions
        safe_list = ['math','acos', 'asin', 'atan', 'atan2', 'ceil', 'cos', 'cosh', 'degrees',\
                     'e', 'exp', 'fabs', 'floor', 'fmod', 'frexp', 'hypot', 'ldexp', 'log',\
                     'log10', 'modf', 'pi', 'pow', 'radians', 'sin', 'sinh', 'sqrt', 'tan', 'tanh']
        #use the list to filter the local namespace
        safe_dict = dict([ (k, locals().get(k, None)) for k in safe_list ])
        #add any needed builtins back in.
        safe_dict['abs'] = abs

        result = eval(arg,{"__builtins__":None},safe_dict)
        reply = "%s = %s " % (arg,result)

        self.respond(reply)


