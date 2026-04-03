const fs = require('fs').promises;
const path = require('path');

class FileScanner {
  constructor() {
    this.defaultExcludes = ['node_modules', '.git', 'dist', 'build', '.cache'];
  }

  async scanFiles(dir, extensions, excludeDirs = this.defaultExcludes) {
    const files = [];
    
    const scan = async (currentDir) => {
      const entries = await fs.readdir(currentDir);
      
      for (const entry of entries) {
        const fullPath = path.join(currentDir, entry);
        const stat = await fs.stat(fullPath);
        
        if (stat.isDirectory()) {
          if (!excludeDirs.includes(entry) && !entry.startsWith('.')) {
            await scan(fullPath);
          }
        } else if (extensions.includes(path.extname(entry))) {
          files.push(fullPath);
        }
      }
    };
    
    await scan(dir);
    return files;
  }

  async readFiles(filePaths) {
    const contents = {};
    for (const filePath of filePaths) {
      try {
        contents[filePath] = await fs.readFile(filePath, 'utf8');
      } catch (err) {
        console.warn(`无法读取文件: ${filePath}`);
      }
    }
    return contents;
  }
}

module.exports = FileScanner;
