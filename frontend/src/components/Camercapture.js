import React, { useState } from "react";

const Cameracapture = () => {
  const [selectedImage, setSelectedImage] = useState(null);
  const [processedImage, setProcessedImage] = useState(null);

  const handleImageUpload = (event) => {
    const file = event.target.files[0];
    setSelectedImage(file);
  };

  const handleSubmit = async () => {
    if (!selectedImage) return;
    
    const formData = new FormData();
    formData.append("image", selectedImage);

    try {
      const response = await fetch("http://localhost:5000/detect", {
        method: "POST",
        body: formData,
      });
      
      if (!response.ok) {
        throw new Error("Failed to process image");
      }

      const blob = await response.blob();
      setProcessedImage(URL.createObjectURL(blob));
    } catch (error) {
      console.error("Error:", error);
    }
  };

  return (
    <div style={{ textAlign: "center", padding: "20px" }}>
      <h1>YOLOv8 Object Detection</h1>
      <input type="file" accept="image/*" onChange={handleImageUpload} />
      <button onClick={handleSubmit} style={{ margin: "10px", padding: "10px" }}>Upload & Detect</button>
      <div style={{ marginTop: "20px" }}>
        {selectedImage && (
          <div>
            <h3>Uploaded Image:</h3>
            <img
              src={URL.createObjectURL(selectedImage)}
              alt="Uploaded"
              style={{ width: "50%", border: "2px solid black", borderRadius: "10px" }}
            />
          </div>
        )}
        {processedImage && (
          <div>
            <h3>Processed Image:</h3>
            <img
              src={processedImage}
              alt="Processed"
              style={{ width: "50%", border: "2px solid green", borderRadius: "10px" }}
            />
          </div>
        )}
      </div>
    </div>
  );
};

export default Cameracapture;
