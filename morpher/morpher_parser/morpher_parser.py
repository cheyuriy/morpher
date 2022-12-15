from enum import Enum 
from ..lexer import Token, Dot, Part

Input = Enum("Input", ["TAKE", "DROP"])
Pointer = Enum("Pointer", ["FULL", "PARTIAL", "FIRST", "LAST", "NTH"])
Transformation = Enum("Transformation", ["ID", "EXTRACT", "FLATTEN", "APPLY", "LOWER", "UPPER"])
Naming = Enum("Naming", ["ALIAS", "PREFIX", "SUFFIX", "SPLIT"])
Casting = Enum("Casting", ["CAST", "SAFE_CAST", "DEFAULT_CAST"])

operation_to_enum = {
    "take": Input.TAKE,
    "drop": Input.DROP,
    "#": Pointer.FULL,
    "#full": Pointer.FULL,
    "#partial": Pointer.PARTIAL,
    "#first": Pointer.FIRST,
    "#last": Pointer.LAST,
    "#nth": Pointer.NTH,
    "!": Transformation.ID,
    "!id": Transformation.ID,
    "!extract": Transformation.EXTRACT,
    "!flatten": Transformation.FLATTEN,
    "!apply": Transformation.APPLY,
    "!lower": Transformation.LOWER,
    "!upper": Transformation.UPPER,
    "@": Naming.ALIAS,
    "@alias": Naming.ALIAS,
    "@prefix": Naming.PREFIX,
    "@suffix": Naming.SUFFIX,
    "@split": Naming.SPLIT,
    "^": Casting.CAST,
    "^cast": Casting.CAST,
    "^safe_cast": Casting.SAFE_CAST,
    "^default_cast": Casting.DEFAULT_CAST
}

operation_type_to_default_command = {
    "Pointer": Pointer.FULL,
    "Transformation": Transformation.ID,
    "Naming": Naming.ALIAS
}

class Operation:
    def __init__(self, operation, *args):
        self.operation = operation
        self.args = args[0] 
        self.operation_type = operation.__class__.__name__

    def __repr__(self):
        args = ", ".join(map(str, self.args))
        return "{} op: {} {}".format(self.operation_type, self.operation, args)

class InputOperation(Operation):
    def __init__(self, operation, *args):
        super().__init__(operation, *args)

    @classmethod
    def new(cls, operation, *args):
        return cls(operation, args)

class PointerOperation(Operation):
    def __init__(self, operation, *args):
        super().__init__(operation, *args) 
    
    @classmethod
    def new(cls, operation, *args):
        return cls(operation, args)

class TransformationOperation(Operation):
    def __init__(self, operation, *args):
        super().__init__(operation, *args) 

    @classmethod
    def new(cls, operation, *args):
        return cls(operation, args)

class NamingOperation(Operation):
    def __init__(self, operation, *args):
        super().__init__(operation, *args) 

    @classmethod
    def new(cls, operation, *args):
        return cls(operation, args)

class CastingOperation(Operation):
    def __init__(self, operation, *args):
        super().__init__(operation, *args) 

    @classmethod
    def new(cls, operation, *args):
        return cls(operation, args)

class OperationFactory:
    @staticmethod
    def default_operation(operation_type):
        operation = operation_type_to_default_command.get(operation_type, None)
        if not operation:
            print("Unknown default for command {}".format(operation_type))
            return None

        if isinstance(operation, Input):
            operation_object = InputOperation.new(operation)
        elif isinstance(operation, Pointer):
            operation_object = PointerOperation.new(operation)
        elif isinstance(operation, Transformation):
            operation_object = TransformationOperation.new(operation)
        elif isinstance(operation, Naming):
            operation_object = NamingOperation.new(operation)
        elif isinstance(operation, Casting):
            operation_object = CastingOperation.new(operation)
        else:
            print("Unknown operation class for {} - no corresponding Operation subclass".format(operation))
            return None

        return operation_object

    @staticmethod
    def from_token(token):
        if isinstance(token, Dot):
            return None
        elif isinstance(token, Part):
            operation = operation_to_enum.get(token[0](), None)
            if not operation:
                print("Unknown token {}".format(token))
                return None 
            
            args = list(map(lambda x: x(), token[1:]))
            if isinstance(operation, Input):
                operation_object = InputOperation.new(operation, args)
            elif isinstance(operation, Pointer):
                operation_object = PointerOperation.new(operation, args)
            elif isinstance(operation, Transformation):
                operation_object = TransformationOperation.new(operation, args)
            elif isinstance(operation, Naming):
                operation_object = NamingOperation.new(operation, args)
            elif isinstance(operation, Casting):
                operation_object = CastingOperation.new(operation, args)
            else:
                print("Unknown operation class for {} - no corresponding Operation subclass".format(operation))
                return None
            
            if not operation_object:
                print("Incorrect construction of {} operation with args {}".format(operation, args))
                return None

            return operation_object 

        elif isinstance(token, Token):
            return None 

class Instruction:
    def __init__(self, operations) -> None:
        self.operations = operations

    def __getitem__(self, i) -> Operation:
        return self.operations[i]

    def __repr__(self):
        operations_string = "\n\t".join(list(map(str, self.operations)))
        return "Instruction:\n\t{}\n".format(operations_string)

class Parser:
    operation_order = ["Input", "Pointer", "Transformation", "Naming", "Casting"]
    
    def _fill_operations(self, prev_operation_type, curr_operation_type):
        if curr_operation_type == self.operation_order[0]:
            return []
            
        prev_operation_idx = self.operation_order.index(prev_operation_type)
        curr_operation_idx = self.operation_order.index(curr_operation_type)
        if curr_operation_idx > prev_operation_idx:
            operation_to_fill = self.operation_order[prev_operation_idx+1:curr_operation_idx]
        elif curr_operation_idx <= prev_operation_idx:
            operation_to_fill = self.operation_order[prev_operation_idx+1:] + self.operation_order[:curr_operation_idx]
        operation_to_fill = list(filter(lambda x: x not in ["Input", "Casting"], operation_to_fill))
        
        results = []
        for item in operation_to_fill:
            operation = OperationFactory().default_operation(item)
            if not operation:
                continue
            results.append(operation)
        
        return results

    def parse(self, tokens):
        instructions = []
        for item in tokens:
            operations = []
            prev_operation_type = None
            for token in item:
                operation = OperationFactory().from_token(token)
                if not operation:
                    continue 

                if not prev_operation_type:
                    prev_operation_type = self.operation_order[0]

                operations += self._fill_operations(prev_operation_type, operation.operation_type)
                operations.append(operation)
                prev_operation_type = operation.operation_type
            instructions.append(Instruction(operations))
        return instructions