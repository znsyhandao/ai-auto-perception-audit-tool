#!/usr/bin/env node

/**
 * 简化发布脚本 - 创建干净的发布包
 */

const fs = require('fs').promises;
const path = require('path');
const { execSync } = require('child_process');

// 项目根目录
const ROOT_DIR = path.resolve(__dirname, '..');
const RELEASE_DIR = path.join(ROOT_DIR, 'release');
const PACKAGE_JSON = require(path.join(ROOT_DIR, 'package.json'));

console.log('🚀 OpenClaw Consistency Checker 发布脚本');
console.log(`版本: ${PACKAGE_JSON.version}`);
console.log('='.repeat(60));

async function runRelease() {
  try {
    // 步骤1: 清理发布目录
    console.log('\n1. 准备发布目录...');
    await prepareReleaseDirectory();
    
    // 步骤2: 复制必需文件
    console.log('\n2. 复制文件...');
    await copyEssentialFiles();
    
    // 步骤3: 创建ZIP包
    console.log('\n3. 创建发布包...');
    const zipPath = await createZipPackage();
    
    // 步骤4: 验证
    console.log('\n4. 验证发布包...');
    await validateRelease(zipPath);
    
    // 完成
    console.log('\n🎉 发布包创建完成！');
    console.log(`   发布包: ${zipPath}`);
    console.log(`   大小: ${(await fs.stat(zipPath)).size} 字节`);
    
    console.log('\n下一步:');
    console.log('   1. 登录 ClawHub: npx clawhub login');
    console.log('   2. 发布插件: npx clawhub publish');
    console.log('   3. 验证安装: npx clawhub install @your-org/openclaw-consistency-checker');
    
  } catch (error) {
    console.error(`❌ 发布失败: ${error.message}`);
    process.exit(1);
  }
}

async function prepareReleaseDirectory() {
  // 删除旧的发布目录
  if (await directoryExists(RELEASE_DIR)) {
    await fs.rm(RELEASE_DIR, { recursive: true, force: true });
  }
  
  // 创建新的发布目录
  await fs.mkdir(RELEASE_DIR, { recursive: true });
  console.log(`   创建发布目录: ${RELEASE_DIR}`);
}

async function copyEssentialFiles() {
  // 必需文件列表
  const essentialFiles = [
    'README.md',
    'LICENSE',
    'package.json',
    'index.js',
    'cli_fixed.js',
    'test_simple.js'
  ];
  
  // 必需目录
  const essentialDirs = [
    'checkers',
    'utils'
  ];
  
  let fileCount = 0;
  let dirCount = 0;
  
  // 复制文件
  for (const file of essentialFiles) {
    const source = path.join(ROOT_DIR, file);
    const target = path.join(RELEASE_DIR, file);
    
    if (await fileExists(source)) {
      await fs.copyFile(source, target);
      fileCount++;
    }
  }
  
  // 复制目录
  for (const dir of essentialDirs) {
    const source = path.join(ROOT_DIR, dir);
    const target = path.join(RELEASE_DIR, dir);
    
    if (await directoryExists(source)) {
      await copyDirectoryWithoutNodeModules(source, target);
      dirCount++;
    }
  }
  
  console.log(`   复制 ${fileCount} 个文件, ${dirCount} 个目录`);
}

async function copyDirectoryWithoutNodeModules(source, target) {
  await fs.mkdir(target, { recursive: true });
  
  const items = await fs.readdir(source);
  
  for (const item of items) {
    // 跳过不需要的文件和目录
    if (item === 'node_modules' || item.startsWith('.') || item.endsWith('.pyc')) {
      continue;
    }
    
    const sourcePath = path.join(source, item);
    const targetPath = path.join(target, item);
    
    const stat = await fs.stat(sourcePath);
    
    if (stat.isDirectory()) {
      await copyDirectoryWithoutNodeModules(sourcePath, targetPath);
    } else {
      await fs.copyFile(sourcePath, targetPath);
    }
  }
}

async function createZipPackage() {
  const version = PACKAGE_JSON.version;
  const zipName = `openclaw-consistency-checker-${version}.zip`;
  const zipPath = path.join(ROOT_DIR, zipName);
  
  // 删除旧的ZIP文件
  if (await fileExists(zipPath)) {
    await fs.unlink(zipPath);
  }
  
  try {
    // 在Windows上使用PowerShell的Compress-Archive
    console.log(`   创建ZIP包: ${zipPath}`);
    
    execSync(`powershell -Command "Compress-Archive -Path '${RELEASE_DIR}\\*' -DestinationPath '${zipPath}' -Force"`, {
      stdio: 'pipe'
    });
    
    return zipPath;
    
  } catch (error) {
    console.log(`   ⚠️ ZIP创建失败，创建目录副本: ${error.message}`);
    
    // 创建目录副本作为备选
    const fallbackDir = path.join(ROOT_DIR, `openclaw-consistency-checker-${version}`);
    if (await directoryExists(fallbackDir)) {
      await fs.rm(fallbackDir, { recursive: true, force: true });
    }
    
    await fs.cp(RELEASE_DIR, fallbackDir, { recursive: true });
    console.log(`   创建发布目录: ${fallbackDir}`);
    
    return fallbackDir;
  }
}

async function validateRelease(releasePath) {
  console.log('   验证发布包内容...');
  
  const requiredFiles = ['README.md', 'package.json', 'index.js', 'cli_fixed.js'];
  let missingFiles = [];
  
  if (releasePath.endsWith('.zip')) {
    // 对于ZIP文件，检查文件大小
    const stats = await fs.stat(releasePath);
    console.log(`   ZIP包大小: ${stats.size} 字节`);
    
    if (stats.size < 1000) {
      console.log('   ⚠️ ZIP包可能为空或太小');
    }
  } else {
    // 对于目录，检查必需文件
    for (const file of requiredFiles) {
      const filePath = path.join(releasePath, file);
      if (await fileExists(filePath)) {
        console.log(`   ✅ ${file} 存在`);
      } else {
        missingFiles.push(file);
        console.log(`   ⚠️ ${file} 缺失`);
      }
    }
  }
  
  if (missingFiles.length === 0) {
    console.log('   ✅ 发布包验证完成');
  } else {
    console.log(`   ⚠️ 缺失文件: ${missingFiles.join(', ')}`);
  }
}

// 工具函数
async function fileExists(filePath) {
  try {
    await fs.access(filePath);
    return true;
  } catch {
    return false;
  }
}

async function directoryExists(dirPath) {
  try {
    const stat = await fs.stat(dirPath);
    return stat.isDirectory();
  } catch {
    return false;
  }
}

// 运行发布脚本
if (require.main === module) {
  runRelease().catch(error => {
    console.error(`❌ 发布脚本失败: ${error.message}`);
    process.exit(1);
  });
}

module.exports = { runRelease };