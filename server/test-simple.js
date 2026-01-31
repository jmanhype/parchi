import express from 'express';
console.log('Express imported');
const app = express();
app.listen(8788, () => console.log('Test server running on 8788'));
