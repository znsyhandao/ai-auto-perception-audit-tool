// Simple consistency checker - English only
class SimpleConsistencyChecker {
  constructor(config) {
    this.config = config;
  }

  async runChecks(skillPath) {
    return {
      fileCount: 1,
      errors: [],
      warnings: ['This is a minimal version for initial release'],
      passed: true
    };
  }
}

module.exports = SimpleConsistencyChecker;
