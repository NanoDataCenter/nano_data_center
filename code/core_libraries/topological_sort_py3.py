
class Topological_Sort(object):

   def __init__(self,get_dependency_fn):
     self.dependency_fn = get_dependency_fn
     self.visited_elements = set()
     self.working_elements = []
     self.past_elements = []
     self.sorted_stack = []
     
   def start(self,element):
       self.visited_elements = set()
       self.working_elements = []
       self.sorted_stack = []
       

       self.working_elements.extend(element)
          
       while len(self.working_elements) > 0:
           #print(self.working_elements)
           
           test_element = self.working_elements[-1]
           
           dependents = self.dependency_fn(test_element)
           if self.check_dependencs(dependents) == True:
               self.visited_elements.add(test_element)
               self.sorted_stack.append(test_element)
               self.working_elements.pop(-1)
           else:
               
               for i in dependents:
                  if i not in self.visited_elements:
                     self.working_elements.append(i)
                 
       return self.sorted_stack
       
       
   def check_dependencs(self,dependents):
      
      for i in dependents:
        if i not in self.visited_elements:
           return False
      return True