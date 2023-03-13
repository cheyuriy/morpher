from enum import Enum 
from typing import List, Optional, Self
from ..lexer import Token, Dot, Part

#Enums for every operation divided by type of operations
Input = Enum("Input", ["TAKE", "DROP"])
Pointer = Enum("Pointer", ["FULL", "PARTIAL", "FIRST", "LAST", "NTH"])
Transformation = Enum("Transformation", ["ID", "EXTRACT", "FLATTEN", "APPLY", "LOWER", "UPPER"])
Naming = Enum("Naming", ["ALIAS", "PREFIX", "SUFFIX", "SPLIT"])
Casting = Enum("Casting", ["CAST", "SAFE_CAST", "DEFAULT_CAST"])

#Dictionary to map operation literal to the exact type of operation (exact enum)
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

#Dictionart to map operation type name to the default operation (enum) for this type
operation_type_to_default_command = {
    "Pointer": Pointer.FULL,
    "Transformation": Transformation.ID,
    "Naming": Naming.ALIAS
}

class Operation:
    def __init__(self, operation: Input | Pointer | Transformation | Naming | Casting, *args: List):
        self.operation = operation
        self.args = args[0] 
        self.operation_type = operation.__class__.__name__

    def __repr__(self):
        args = ", ".join(map(str, self.args))
        return "{} op: {} {}".format(self.operation_type, self.operation, args)

class InputOperation(Operation):
    def __init__(self, operation: Input, *args: List):
        super().__init__(operation, *args)

    @classmethod
    def new(cls, operation: Input, *args: List) -> Self:
        return cls(operation, args)

class PointerOperation(Operation):
    def __init__(self, operation: Input, *args: List):
        super().__init__(operation, *args) 
    
    @classmethod
    def new(cls, operation: Input, *args: List) -> Self:
        return cls(operation, args)

class TransformationOperation(Operation):
    def __init__(self, operation: Input, *args: List):
        super().__init__(operation, *args) 

    @classmethod
    def new(cls, operation: Input, *args: List) -> Self:
        return cls(operation, args)

class NamingOperation(Operation):
    def __init__(self, operation: Input, *args: List):
        super().__init__(operation, *args) 

    @classmethod
    def new(cls, operation: Input, *args: List) -> Self:
        return cls(operation, args)

class CastingOperation(Operation):
    def __init__(self, operation: Input, *args: List):
        super().__init__(operation, *args) 

    @classmethod
    def new(cls, operation: Input, *args: List) -> Self:
        return cls(operation, args)

class OperationFactory:
    """ Factory class to instantiate Operations
    """

    @staticmethod
    def default_operation(operation_type: str) -> Operation:
        """Instantiate default Operation for the particular type

        Args:
            operation_type (str): name of the type

        Raises:
            ValueError: can't finf default operation for the provided type name
            ValueError: default operation class is unknown

        Returns:
            Optional[Operation]: default operation for this type
        """

        operation = operation_type_to_default_command.get(operation_type, None)
        if not operation:
            raise ValueError("Can't instantiate default operation for type name {}".format(operation_type))

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
            raise ValueError("Unknown operation class for {} - no corresponding Operation subclass".format(operation))

        return operation_object

    @staticmethod
    def from_token(token: Token) -> Optional[Operation]:
        #no need to instantiate any operation for the Dot token
        if isinstance(token, Dot):
            return None

        elif isinstance(token, Part):
            #first token in a Part defines an operation
            operation = operation_to_enum.get(token[0](), None)
            if not operation:
                raise ValueError("Can't instantiate an operation for the token '{}'".format(token))
            
            #all other tokens in a Part are arguments for this operation
            args = list(map(lambda x: x(), token[1:]))

            #instantiating and providing arguments
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
                raise ValueError("Unknown operation class for {} - no corresponding Operation subclass".format(operation))

            return operation_object 

        #no need to instantiate any operation for any other Token class
        elif isinstance(token, Token):
            return None 

class Instruction:
    """ Instruction object.
    Instruction is a distinct operation with one field. It contains:
    - 1 Input operation
    - 0-N Pointer/Transformation/Naming operations
    - 0-1 Casting operation
    It's a list of Operations under the hood.
    """
    def __init__(self, operations) -> None:
        self.operations = operations

    def __getitem__(self, i) -> Operation:
        return self.operations[i]

    def __repr__(self):
        operations_string = "\n\t".join(list(map(str, self.operations)))
        return "Instruction:\n\t{}\n".format(operations_string)

class Parser:
    """Parser of Tokens
    Transforms list of tokens into the sequence of Instructions to perform on an input data
    """

    # Operations in a particular instruction should follow a pattern
    # Each Instruction should start from `Input` Operation and be followed by other operations as present in this list (maybe repeating the cycle more than once)
    operation_order = ["Input", "Pointer", "Transformation", "Naming", "Casting"]
    
    def _fill_operations(self, prev_operation_type: str, curr_operation_type: str) -> List[Operation]:
        """Fill the gaps between two operations according to the cycle of operations (see operation_order class variable)

        Args:
            prev_operation_type (str): name of the type of the previous operation
            curr_operation_type (str): name of the type of the current operation

        Returns:
            List[Operation]: List of operations to be added before current operation to fullfil the cycle
        """

        #We don't need to fill anything if current operation is the first in the order
        if curr_operation_type == self.operation_order[0]:
            return []
            
        #Rules to fill the gap:
        #- If current operation is more to the right of the previous then we add all operations between them
        #- If current operation is more to the left of the previous then we are moving in the cycle and adding operations until we encounter current operation
        #- If current operation is the same as previous, then we will ad the full cycle of operations
        #- In the end we remove all Input and Casting operations, because there should be only one such operation in every instruction
        prev_operation_idx = self.operation_order.index(prev_operation_type)
        curr_operation_idx = self.operation_order.index(curr_operation_type)
        if curr_operation_idx > prev_operation_idx:
            operation_to_fill = self.operation_order[prev_operation_idx+1:curr_operation_idx]
        elif curr_operation_idx <= prev_operation_idx:
            operation_to_fill = self.operation_order[prev_operation_idx+1:] + self.operation_order[:curr_operation_idx]
        operation_to_fill = list(filter(lambda x: x not in ["Input", "Casting"], operation_to_fill))

        #We are instantiating each added operation
        results = []
        for item in operation_to_fill:
            operation = OperationFactory().default_operation(item)
            results.append(operation)
        
        return results

    def parse(self, parts: List[Part]) -> List[Instruction]:
        """Parses list of Parts into list of Instructions consisting of Operations
        During parsing we strictly follow the cycle of commands (see operation_order class variable) and filling the gaps with a default Operations of absent Type

        Args:
            parts (List[Part]): list of Parts from lexer

        Returns:
            List[Instruction]: list of Instructions
        """

        instructions = []
        for part in parts:
            operations = []

            #we always remember type of previous operation to be able to fill the gaps according to the cycle of operations' types
            prev_operation_type = None
            for token in part:
                #in case of uknown token we'll encounter an exception here
                operation = OperationFactory().from_token(token)

                #operation is None only for the case if Token is not an instance of Part object
                #in other words, it doesn't contain any actual action
                if not operation:
                    continue 

                #if there are no previous tokens, then we suppose that the previous operation is the first one in the order
                if not prev_operation_type:
                    prev_operation_type = self.operation_order[0]

                #filling the gaps between prev_operation_type and current operation type
                operations += self._fill_operations(prev_operation_type, operation.operation_type)

                operations.append(operation)
                prev_operation_type = operation.operation_type
            instructions.append(Instruction(operations))
        return instructions