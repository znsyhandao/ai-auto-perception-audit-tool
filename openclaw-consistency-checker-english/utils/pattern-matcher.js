class PatternMatcher {
  constructor(patterns) {
    this.patterns = patterns.map(p => new RegExp(p, 'i'));
  }

  match(content) {
    const matches = [];
    for (const pattern of this.patterns) {
      const found = content.match(pattern);
      if (found) matches.push(...found);
    }
    return [...new Set(matches)];
  }

  matchAll(contents) {
    const results = {};
    for (const [filePath, content] of Object.entries(contents)) {
      const matches = this.match(content);
      if (matches.length > 0) {
        results[filePath] = matches;
      }
    }
    return results;
  }
}

module.exports = PatternMatcher;

