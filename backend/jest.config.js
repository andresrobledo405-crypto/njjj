export default {
  testEnvironment: 'node',
  testMatch: ['**/tests/**/*.test.js'],
  collectCoverageFrom: ['**/*.js', '!node_modules/**', '!tests/**'],
  transformIgnorePatterns: ['node_modules/'],
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
};
