export const validateEmail = (email) => {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return re.test(email);
};

export const validatePassword = (password) => {
  return password && password.length >= 8;
};

export const validateFileSize = (sizeInBytes) => {
  const maxSize = 2 * 1024 * 1024 * 1024; // 2GB
  return sizeInBytes <= maxSize;
};

export const validateVideoFormat = (filename) => {
  const allowedFormats = ['.mp4', '.mov', '.webm'];
  const ext = filename.toLowerCase().slice(-4);
  return allowedFormats.includes(ext);
};
