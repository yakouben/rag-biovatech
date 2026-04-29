import { Platform } from 'react-native';

export const COLORS = {
  primary: '#00B4DB',
  primaryDark: '#0083B0',
  background: '#F0F8FF',
  white: '#FFFFFF',
  text: '#1A1A1A',
  textSecondary: '#666666',
  glass: 'rgba(255, 255, 255, 0.2)',
  glassBorder: 'rgba(255, 255, 255, 0.5)',
  success: '#2ECC71',
  warning: '#F1C40F',
  danger: '#E74C3C',
};

export const FONTS = {
  bold: Platform.OS === 'ios' ? 'HelveticaNeue-Bold' : 'sans-serif-condensed',
  semibold: Platform.OS === 'ios' ? 'HelveticaNeue-Medium' : 'sans-serif-medium',
  medium: Platform.OS === 'ios' ? 'Helvetica-Light' : 'sans-serif-light',
  regular: Platform.OS === 'ios' ? 'Helvetica' : 'sans-serif',
  arabic: Platform.OS === 'ios' ? 'GeezaPro' : 'serif', // Good Arabic fallback on iOS
};
