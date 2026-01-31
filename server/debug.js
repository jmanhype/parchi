console.log('Wrapper starting');
try {
  await import('./dist/src/index.js');
  console.log('Import done');
} catch (e) {
  console.error('Import failed', e);
}
