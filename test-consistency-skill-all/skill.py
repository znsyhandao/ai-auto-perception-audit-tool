'''Test skill with issues'''
import subprocess
import requests

version = '1.0.3'

class TestSkill:
    def __init__(self):
        self.name = 'test-skill'
    
    def run(self):
        # Dangerous eval usage
        result = eval('2 + 2')
        return result