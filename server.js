const express = require('express');
const bodyParser = require('body-parser');
const multer = require('multer');
const fs = require('fs');
const path = require('path');

const app = express();
const port = process.env.PORT || 3000;

// Configure static file serving for the public directory
app.use(express.static(path.join(__dirname, 'public')));

// Configure body-parser for handling JSON data
app.use(bodyParser.json());

// Configure multer for file uploads
const storage = multer.diskStorage({
  destination: function (req, file, cb) {
    cb(null, 'uploads'); // Create an 'uploads' directory to store uploaded files
  },
  filename: function (req, file, cb) {
    cb(null, file.originalname);
  },
});

const upload = multer({ storage: storage });

// Define a route to list images in the 'screenshots' folder
app.get('/get_images', (req, res) => {
  const folder = 'screenshots/';
  fs.readdir(folder, (err, files) => {
    if (err) {
      console.error(err);
      res.status(500).json({ error: 'Internal Server Error' });
      return;
    }

    const imageFiles = files.filter((file) =>
      /\.(jpg|jpeg|png|gif)$/i.test(file)
    );

    res.json(imageFiles);
  });
});

app.listen(port, () => {
  console.log(`Server is running on port ${port}`);
});
