# Implementation Examples

**Version:** 1.0
**Date:** November 6, 2025

Complete implementation examples for mobile-first image-to-image transfer applications across different frameworks.

---

## Table of Contents

1. [HTML/CSS/JavaScript](#htmlcssjavascript)
2. [React/React Native](#reactreact-native)
3. [Flutter](#flutter)
4. [Swift/SwiftUI](#swiftswiftui)
5. [Best Practices](#best-practices)

---

## HTML/CSS/JavaScript

### Complete Image Upload Page

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <title>Image Transfer</title>

  <style>
    /* Design System Variables */
    :root {
      /* Colors */
      --purple-600: #7C3AED;
      --purple-700: #6D28D9;
      --gray-50: #F9FAFB;
      --gray-100: #F3F4F6;
      --gray-200: #E5E7EB;
      --gray-600: #4B5563;
      --gray-900: #111827;
      --white: #FFFFFF;

      /* Spacing */
      --space-2: 8px;
      --space-3: 12px;
      --space-4: 16px;
      --space-6: 24px;

      /* Border Radius */
      --radius-base: 8px;
      --radius-lg: 16px;
      --radius-full: 9999px;

      /* Shadows */
      --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.1);
      --shadow-md: 0 10px 15px rgba(0, 0, 0, 0.1);

      /* Typography */
      --text-base: 16px;
      --text-sm: 14px;
      --font-semibold: 600;

      /* Animation */
      --duration-fast: 200ms;
      --ease-out: cubic-bezier(0, 0, 0.2, 1);
    }

    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }

    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      background: var(--gray-50);
      color: var(--gray-900);
      line-height: 1.5;
      padding-bottom: 72px; /* Space for bottom nav */
    }

    .container {
      max-width: 600px;
      margin: 0 auto;
      padding: var(--space-4);
    }

    .upload-area {
      position: relative;
      width: 100%;
      min-height: 300px;
      border: 2px dashed var(--gray-200);
      border-radius: var(--radius-lg);
      background: var(--white);
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: var(--space-6);
      gap: var(--space-4);
      cursor: pointer;
      transition: all var(--duration-fast) var(--ease-out);
    }

    .upload-area:hover,
    .upload-area.dragover {
      border-color: var(--purple-600);
      background: rgba(124, 58, 237, 0.05);
    }

    .upload-icon {
      width: 48px;
      height: 48px;
      color: var(--purple-600);
    }

    .upload-title {
      font-size: var(--text-base);
      font-weight: var(--font-semibold);
      color: var(--gray-900);
    }

    .upload-subtitle {
      font-size: var(--text-sm);
      color: var(--gray-600);
      text-align: center;
    }

    .upload-input {
      position: absolute;
      inset: 0;
      opacity: 0;
      cursor: pointer;
    }

    .button-primary {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: var(--space-2);
      padding: var(--space-3) var(--space-6);
      min-height: 44px;
      font-size: var(--text-base);
      font-weight: var(--font-semibold);
      color: var(--white);
      background: var(--purple-600);
      border: none;
      border-radius: var(--radius-base);
      cursor: pointer;
      transition: all var(--duration-fast) var(--ease-out);
      box-shadow: var(--shadow-sm);
    }

    .button-primary:hover {
      background: var(--purple-700);
      box-shadow: var(--shadow-md);
    }

    .button-primary:active {
      transform: scale(0.98);
    }

    .preview {
      display: none;
      margin-top: var(--space-4);
      border-radius: var(--radius-lg);
      overflow: hidden;
      box-shadow: var(--shadow-sm);
    }

    .preview.visible {
      display: block;
      animation: fade-in 300ms ease-out;
    }

    .preview img {
      width: 100%;
      height: auto;
      display: block;
    }

    @keyframes fade-in {
      from {
        opacity: 0;
        transform: translateY(10px);
      }
      to {
        opacity: 1;
        transform: translateY(0);
      }
    }

    /* Bottom Navigation */
    .bottom-nav {
      position: fixed;
      bottom: 0;
      left: 0;
      right: 0;
      height: 56px;
      padding-bottom: env(safe-area-inset-bottom);
      background: var(--white);
      border-top: 1px solid var(--gray-200);
      box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.05);
      display: flex;
      justify-content: space-around;
      z-index: 100;
    }

    .bottom-nav__item {
      flex: 1;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: 2px;
      color: var(--gray-600);
      text-decoration: none;
      font-size: 12px;
      transition: color var(--duration-fast);
    }

    .bottom-nav__item--active {
      color: var(--purple-600);
    }

    .bottom-nav__icon {
      width: 24px;
      height: 24px;
    }
  </style>
</head>
<body>
  <div class="container">
    <h1 style="margin-bottom: 24px; font-size: 32px; font-weight: 700;">
      Upload Image
    </h1>

    <div class="upload-area" id="uploadArea">
      <input
        type="file"
        accept="image/*"
        class="upload-input"
        id="fileInput"
        aria-label="Upload image"
      >

      <svg class="upload-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"/>
      </svg>

      <div class="upload-title">Drop your image here</div>
      <div class="upload-subtitle">or tap to browse</div>

      <button class="button-primary" type="button">
        Choose File
      </button>
    </div>

    <div class="preview" id="preview">
      <img id="previewImage" alt="Preview">
    </div>
  </div>

  <!-- Bottom Navigation -->
  <nav class="bottom-nav">
    <a href="#" class="bottom-nav__item">
      <svg class="bottom-nav__icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/>
      </svg>
      <span>Home</span>
    </a>

    <a href="#" class="bottom-nav__item bottom-nav__item--active">
      <svg class="bottom-nav__icon" fill="currentColor" viewBox="0 0 24 24">
        <path d="M12 4v16m8-8H4"/>
      </svg>
      <span>Upload</span>
    </a>

    <a href="#" class="bottom-nav__item">
      <svg class="bottom-nav__icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/>
      </svg>
      <span>Gallery</span>
    </a>

    <a href="#" class="bottom-nav__item">
      <svg class="bottom-nav__icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
      </svg>
      <span>Profile</span>
    </a>
  </nav>

  <script>
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');
    const preview = document.getElementById('preview');
    const previewImage = document.getElementById('previewImage');

    // File input change
    fileInput.addEventListener('change', (e) => {
      handleFiles(e.target.files);
    });

    // Drag and drop
    uploadArea.addEventListener('dragover', (e) => {
      e.preventDefault();
      uploadArea.classList.add('dragover');
    });

    uploadArea.addEventListener('dragleave', () => {
      uploadArea.classList.remove('dragover');
    });

    uploadArea.addEventListener('drop', (e) => {
      e.preventDefault();
      uploadArea.classList.remove('dragover');
      handleFiles(e.dataTransfer.files);
    });

    function handleFiles(files) {
      if (files.length === 0) return;

      const file = files[0];

      // Validate file type
      if (!file.type.startsWith('image/')) {
        alert('Please select an image file');
        return;
      }

      // Show preview
      const reader = new FileReader();
      reader.onload = (e) => {
        previewImage.src = e.target.result;
        preview.classList.add('visible');

        // Haptic feedback (if supported)
        if ('vibrate' in navigator) {
          navigator.vibrate(10);
        }
      };
      reader.readAsDataURL(file);
    }
  </script>
</body>
</html>
```

---

## React/React Native

### React Component Example

```jsx
// ImageUpload.jsx
import React, { useState, useRef } from 'react';
import './ImageUpload.css';

export function ImageUpload({ onImageSelect }) {
  const [preview, setPreview] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef(null);

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    processFile(file);
  };

  const handleDrop = (event) => {
    event.preventDefault();
    setIsDragging(false);

    const file = event.dataTransfer.files[0];
    processFile(file);
  };

  const processFile = (file) => {
    if (!file || !file.type.startsWith('image/')) {
      alert('Please select an image file');
      return;
    }

    // Create preview
    const reader = new FileReader();
    reader.onload = (e) => {
      setPreview(e.target.result);
      onImageSelect?.(file, e.target.result);
    };
    reader.readAsDataURL(file);

    // Haptic feedback
    if ('vibrate' in navigator) {
      navigator.vibrate(10);
    }
  };

  return (
    <div className="image-upload">
      <div
        className={`upload-area ${isDragging ? 'dragover' : ''}`}
        onDragOver={(e) => {
          e.preventDefault();
          setIsDragging(true);
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          onChange={handleFileSelect}
          className="upload-input"
          aria-label="Upload image"
        />

        <UploadIcon className="upload-icon" />
        <h3 className="upload-title">Drop your image here</h3>
        <p className="upload-subtitle">or tap to browse</p>

        <button className="button-primary" type="button">
          Choose File
        </button>
      </div>

      {preview && (
        <div className="preview visible">
          <img src={preview} alt="Preview" />
        </div>
      )}
    </div>
  );
}

// Icon component
function UploadIcon({ className }) {
  return (
    <svg
      className={className}
      fill="none"
      stroke="currentColor"
      viewBox="0 0 24 24"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={2}
        d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
      />
    </svg>
  );
}
```

### React Native Component

```jsx
// ImageUploadRN.jsx
import React, { useState } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  Image,
  StyleSheet,
  Platform,
  Vibration,
} from 'react-native';
import * as ImagePicker from 'expo-image-picker';

export function ImageUploadRN({ onImageSelect }) {
  const [image, setImage] = useState(null);

  const pickImage = async (source) => {
    // Haptic feedback
    if (Platform.OS === 'ios' || Platform.OS === 'android') {
      Vibration.vibrate(10);
    }

    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: true,
      aspect: [1, 1],
      quality: 0.8,
    });

    if (!result.canceled) {
      setImage(result.assets[0].uri);
      onImageSelect?.(result.assets[0]);
    }
  };

  const takePhoto = async () => {
    // Request permission
    const permission = await ImagePicker.requestCameraPermissionsAsync();

    if (permission.granted) {
      const result = await ImagePicker.launchCameraAsync({
        allowsEditing: true,
        aspect: [1, 1],
        quality: 0.8,
      });

      if (!result.canceled) {
        setImage(result.assets[0].uri);
        onImageSelect?.(result.assets[0]);
      }
    }
  };

  return (
    <View style={styles.container}>
      <View style={styles.uploadArea}>
        <Text style={styles.title}>Select Image</Text>
        <Text style={styles.subtitle}>Choose from library or take a photo</Text>

        <View style={styles.buttonGroup}>
          <TouchableOpacity
            style={styles.buttonPrimary}
            onPress={pickImage}
            activeOpacity={0.8}
          >
            <Text style={styles.buttonText}>Choose from Library</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.buttonSecondary}
            onPress={takePhoto}
            activeOpacity={0.8}
          >
            <Text style={styles.buttonTextSecondary}>Take Photo</Text>
          </TouchableOpacity>
        </View>
      </View>

      {image && (
        <Image
          source={{ uri: image }}
          style={styles.preview}
          resizeMode="cover"
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    padding: 16,
  },
  uploadArea: {
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: 24,
    alignItems: 'center',
    ...Platform.select({
      ios: {
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.1,
        shadowRadius: 4,
      },
      android: {
        elevation: 2,
      },
    }),
  },
  title: {
    fontSize: 20,
    fontWeight: '600',
    color: '#111827',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 14,
    color: '#6B7280',
    textAlign: 'center',
    marginBottom: 24,
  },
  buttonGroup: {
    width: '100%',
    gap: 12,
  },
  buttonPrimary: {
    backgroundColor: '#7C3AED',
    borderRadius: 8,
    paddingVertical: 12,
    paddingHorizontal: 24,
    minHeight: 44,
    alignItems: 'center',
    justifyContent: 'center',
  },
  buttonSecondary: {
    backgroundColor: '#FFFFFF',
    borderRadius: 8,
    paddingVertical: 12,
    paddingHorizontal: 24,
    minHeight: 44,
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 2,
    borderColor: '#7C3AED',
  },
  buttonText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#FFFFFF',
  },
  buttonTextSecondary: {
    fontSize: 16,
    fontWeight: '600',
    color: '#7C3AED',
  },
  preview: {
    width: '100%',
    height: 300,
    marginTop: 16,
    borderRadius: 16,
  },
});
```

---

## Flutter

### Flutter Widget Example

```dart
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:image_picker/image_picker.dart';
import 'dart:io';

class ImageUploadWidget extends StatefulWidget {
  final Function(File)? onImageSelected;

  const ImageUploadWidget({Key? key, this.onImageSelected}) : super(key: key);

  @override
  State<ImageUploadWidget> createState() => _ImageUploadWidgetState();
}

class _ImageUploadWidgetState extends State<ImageUploadWidget> {
  File? _image;
  final ImagePicker _picker = ImagePicker();

  Future<void> _pickImage(ImageSource source) async {
    try {
      // Haptic feedback
      HapticFeedback.lightImpact();

      final XFile? image = await _picker.pickImage(
        source: source,
        maxWidth: 1920,
        maxHeight: 1920,
        imageQuality: 80,
      );

      if (image != null) {
        setState(() {
          _image = File(image.path);
        });

        widget.onImageSelected?.call(_image!);
      }
    } catch (e) {
      // Handle error
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error picking image: $e')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Container(
            padding: const EdgeInsets.all(24),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(16),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withOpacity(0.1),
                  blurRadius: 4,
                  offset: const Offset(0, 2),
                ),
              ],
            ),
            child: Column(
              children: [
                Icon(
                  Icons.cloud_upload_outlined,
                  size: 48,
                  color: Theme.of(context).primaryColor,
                ),
                const SizedBox(height: 16),
                const Text(
                  'Upload Image',
                  style: TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.w600,
                    color: Color(0xFF111827),
                  ),
                ),
                const SizedBox(height: 8),
                const Text(
                  'Choose from library or take a photo',
                  style: TextStyle(
                    fontSize: 14,
                    color: Color(0xFF6B7280),
                  ),
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 24),

                // Primary Button
                ElevatedButton(
                  onPressed: () => _pickImage(ImageSource.gallery),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF7C3AED),
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(
                      vertical: 12,
                      horizontal: 24,
                    ),
                    minimumSize: const Size(double.infinity, 44),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(8),
                    ),
                    elevation: 2,
                  ),
                  child: const Text(
                    'Choose from Library',
                    style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ),

                const SizedBox(height: 12),

                // Secondary Button
                OutlinedButton(
                  onPressed: () => _pickImage(ImageSource.camera),
                  style: OutlinedButton.styleFrom(
                    foregroundColor: const Color(0xFF7C3AED),
                    side: const BorderSide(
                      color: Color(0xFF7C3AED),
                      width: 2,
                    ),
                    padding: const EdgeInsets.symmetric(
                      vertical: 12,
                      horizontal: 24,
                    ),
                    minimumSize: const Size(double.infinity, 44),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(8),
                    ),
                  ),
                  child: const Text(
                    'Take Photo',
                    style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ),
              ],
            ),
          ),

          // Preview
          if (_image != null) ...[
            const SizedBox(height: 16),
            ClipRRect(
              borderRadius: BorderRadius.circular(16),
              child: Image.file(
                _image!,
                height: 300,
                fit: BoxFit.cover,
              ),
            ),
          ],
        ],
      ),
    );
  }
}
```

---

## Swift/SwiftUI

### SwiftUI View Example

```swift
import SwiftUI
import PhotosUI

struct ImageUploadView: View {
    @State private var selectedItem: PhotosPickerItem?
    @State private var selectedImage: Image?
    @State private var showCamera = false

    var body: some View {
        VStack(spacing: 16) {
            // Upload Area
            VStack(spacing: 24) {
                Image(systemName: "cloud.arrow.up")
                    .font(.system(size: 48))
                    .foregroundColor(.purple)

                VStack(spacing: 8) {
                    Text("Upload Image")
                        .font(.title2)
                        .fontWeight(.semibold)

                    Text("Choose from library or take a photo")
                        .font(.subheadline)
                        .foregroundColor(.gray)
                        .multilineTextAlignment(.center)
                }

                VStack(spacing: 12) {
                    // Photo Library Button
                    PhotosPicker(
                        selection: $selectedItem,
                        matching: .images
                    ) {
                        Text("Choose from Library")
                            .font(.body)
                            .fontWeight(.semibold)
                            .foregroundColor(.white)
                            .frame(maxWidth: .infinity)
                            .frame(height: 44)
                            .background(Color.purple)
                            .cornerRadius(8)
                    }
                    .onChange(of: selectedItem) { _ in
                        Task {
                            if let data = try? await selectedItem?.loadTransferable(type: Data.self),
                               let uiImage = UIImage(data: data) {
                                selectedImage = Image(uiImage: uiImage)

                                // Haptic feedback
                                let generator = UIImpactFeedbackGenerator(style: .light)
                                generator.impactOccurred()
                            }
                        }
                    }

                    // Camera Button
                    Button(action: {
                        showCamera = true
                    }) {
                        Text("Take Photo")
                            .font(.body)
                            .fontWeight(.semibold)
                            .foregroundColor(.purple)
                            .frame(maxWidth: .infinity)
                            .frame(height: 44)
                            .background(Color.white)
                            .overlay(
                                RoundedRectangle(cornerRadius: 8)
                                    .stroke(Color.purple, lineWidth: 2)
                            )
                    }
                }
            }
            .padding(24)
            .background(Color.white)
            .cornerRadius(16)
            .shadow(color: Color.black.opacity(0.1), radius: 4, x: 0, y: 2)

            // Preview
            if let selectedImage = selectedImage {
                selectedImage
                    .resizable()
                    .aspectRatio(contentMode: .fill)
                    .frame(height: 300)
                    .cornerRadius(16)
                    .clipped()
                    .transition(.opacity)
            }
        }
        .padding(16)
        .sheet(isPresented: $showCamera) {
            ImagePicker(image: $selectedImage, sourceType: .camera)
        }
    }
}

// Image Picker for Camera
struct ImagePicker: UIViewControllerRepresentable {
    @Binding var image: Image?
    var sourceType: UIImagePickerController.SourceType

    func makeUIViewController(context: Context) -> UIImagePickerController {
        let picker = UIImagePickerController()
        picker.sourceType = sourceType
        picker.delegate = context.coordinator
        return picker
    }

    func updateUIViewController(_ uiViewController: UIImagePickerController, context: Context) {}

    func makeCoordinator() -> Coordinator {
        Coordinator(self)
    }

    class Coordinator: NSObject, UIImagePickerControllerDelegate, UINavigationControllerDelegate {
        let parent: ImagePicker

        init(_ parent: ImagePicker) {
            self.parent = parent
        }

        func imagePickerController(
            _ picker: UIImagePickerController,
            didFinishPickingMediaWithInfo info: [UIImagePickerController.InfoKey: Any]
        ) {
            if let uiImage = info[.originalImage] as? UIImage {
                parent.image = Image(uiImage: uiImage)

                // Haptic feedback
                let generator = UIImpactFeedbackGenerator(style: .light)
                generator.impactOccurred()
            }

            picker.dismiss(animated: true)
        }
    }
}
```

---

## Best Practices

### Performance Optimization

```javascript
// Lazy load images
const ImageWithPlaceholder = ({ src, alt }) => {
  const [loaded, setLoaded] = useState(false);

  return (
    <div className="image-container">
      {!loaded && <div className="shimmer-placeholder" />}
      <img
        src={src}
        alt={alt}
        onLoad={() => setLoaded(true)}
        style={{ display: loaded ? 'block' : 'none' }}
        loading="lazy"
      />
    </div>
  );
};
```

### Responsive Image Loading

```javascript
// Use srcset for responsive images
<img
  srcset="
    image-320w.jpg 320w,
    image-640w.jpg 640w,
    image-960w.jpg 960w,
    image-1280w.jpg 1280w
  "
  sizes="
    (max-width: 320px) 280px,
    (max-width: 640px) 600px,
    (max-width: 960px) 920px,
    1280px
  "
  src="image-640w.jpg"
  alt="Responsive image"
/>
```

### Accessibility

```jsx
// Proper ARIA labels and roles
<button
  onClick={handleUpload}
  aria-label="Upload image"
  aria-describedby="upload-hint"
>
  <UploadIcon aria-hidden="true" />
  <span>Upload</span>
</button>
<p id="upload-hint" className="sr-only">
  Supported formats: JPEG, PNG, WebP. Maximum size: 10MB.
</p>
```

---

**Complete implementation documentation. Ready for production use.**
