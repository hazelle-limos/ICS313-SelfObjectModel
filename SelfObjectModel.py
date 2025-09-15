from collections import deque

class SelfObjectModel:
    def __init__(self, slots=None, parent_slots=None, messages=None, primitive_value=None, primitive_function=None):
        self.slots = slots or {}
        self.parent_slots = parent_slots or []
        self.messages = messages or []
        self.primitive_value = primitive_value
        self.primitive_function = primitive_function

    # Capabilities
    def evaluate(self):
        # Copy self, send each message to the copy, return the last result
        if self.messages:
            obj_copy = self.copy()
            result = None
            for message in self.messages:
                result = obj_copy.send_message(message)
            return result
        # If there is no message, but has a primitive function or value, return those
        elif self.primitive_function is not None:
            return self.primitive_function(self.copy())
        elif self.primitive_value is not None:
            return self.copy()
        # Return self if nothing else to evaluate
        else:
            return self
        
    def copy(self):
        # Slots, parent slots, and messages are shallow-copied, while primitive values/functions are preserved
        return SelfObjectModel(
            slots=self.slots.copy(),
            parent_slots=self.parent_slots.copy(),
            messages=self.messages.copy(),
            primitive_value=self.primitive_value,
            primitive_function=self.primitive_function
        )
    
    def send_message(self, message):
        # BFS lookup for message in slots and parent slots, then evaluate the found object
        target_obj = self._bfs_lookup(message)
        if target_obj is None:
            raise ValueError(f"Message '{message}' not found in slots or parent slots.")
        return target_obj.evaluate()
        
    def send_message_with_parameters(self, message, parameter):
        # BFS lookup for message in slots and parent slots, assign 'parameter' slot, then evaluate
        target_obj = self._bfs_lookup(message)
        if target_obj is None:
            raise ValueError(f"Message '{message}' not found in slots or parent slots.")
        target_copy = target_obj.copy()
        target_copy.assign_slot("parameter", parameter)
        return target_copy.evaluate()
    
    def assign_slot(self, name, obj):
        # Assign or update a slot on this object
        self.slots[name] = obj

    def make_parent(self, name):
        # Make an existing slot a parent slot
        if name in self.slots:
            self.parent_slots.append(self.slots[name])
        else:
            raise ValueError(f"Slot '{name}' does not exist.")
        
    def assign_parent_slot(self, name, obj):
        # Assign a slot and make it a parent in one step
        self.assign_slot(name, obj)
        self.make_parent(name)

    def print(self):
        # Return string representation
        return str(self)

    def __str__(self):
        # Print the primitive value if it exists
        if self.primitive_value is not None:
            return str(self.primitive_value)
        # Print an indication of primitive function if it exists
        if self.primitive_function is not None:
            return "<SelfObjectModel: primitive_function>"
        # Print messages and slots
        if self.messages:
            return f"<SelfObjectModel: messages={self.messages}, slots={list(self.slots.keys())}>"
        # Plain object with no primitive value/function or messages
        return f"<SelfObjectModel: slots={list(self.slots.keys())}>"
        
    # Helpers
    def _bfs_lookup(self, message):
        # BFS to find the message in slots or parent slots
        # Start from self; if not found, check parent slots
        queue = deque([self])
        visited = set()

        while queue:
            current = queue.popleft()
            cid = id(current)
            if cid in visited:
                continue
            visited.add(cid)

            if message in current.slots:
                return current.slots[message]
            
            for p in current.parent_slots:
                if id(p) not in visited:
                    queue.append(p)

        return None
        
# 1) evaluate
obj1 = SelfObjectModel(messages=["say"], slots={"say": SelfObjectModel(primitive_value="hi")})
print(obj1.evaluate())  # hi

# 2) copy
obj2 = SelfObjectModel(slots={"a": SelfObjectModel(primitive_value=1)})
obj3 = obj2.copy(); obj3.assign_slot("b", SelfObjectModel(primitive_value=2))
print(list(obj2.slots), list(obj3.slots))  # ['a'] ['a', 'b']

# 3) send_message
obj4 = SelfObjectModel(slots={"name": SelfObjectModel(primitive_value="Alice")})
print(obj4.send_message("name"))  # Alice

# 4) send_message_with_parameters
def echo(call_obj): 
    return call_obj.slots["parameter"]
obj5 = SelfObjectModel(slots={"echo": SelfObjectModel(primitive_function=echo)})
obj6 = SelfObjectModel(primitive_value="Hello")
print(obj5.send_message_with_parameters("echo", obj6))  # Hello

# 5) assign_slot
obj7 = SelfObjectModel(); obj7.assign_slot("n", SelfObjectModel(primitive_value=7))
print(obj7.send_message("n"))  # 7

# 6) make_parent
obj8 = SelfObjectModel(slots={"color": SelfObjectModel(primitive_value="blue")})
obj9 = SelfObjectModel(); obj9.assign_slot("p", obj8); obj9.make_parent("p")
print(obj9.send_message("color"))  # blue

# 7) assign_parent_slot
obj10 = SelfObjectModel(slots={"age": SelfObjectModel(primitive_value=30)})
obj11 = SelfObjectModel(); obj11.assign_parent_slot("parent", obj10)
print(obj11.send_message("age"))  # 30

# 8) print
obj12 = SelfObjectModel(slots={"x": SelfObjectModel(primitive_value=1)})
print(obj12.print())  # <SelfObjectModel: slots=['x']>
