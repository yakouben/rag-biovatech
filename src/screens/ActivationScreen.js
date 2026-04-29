import React, { useState, useEffect } from 'react';
import { 
  View, Text, StyleSheet, TextInput, 
  TouchableOpacity, ActivityIndicator, Dimensions,
  Platform, StatusBar
} from 'react-native';
import { CameraView, useCameraPermissions } from 'expo-camera';
import { Ionicons } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';
import usePatientStore from '../store/usePatientStore';
import GlassCard from '../components/GlassCard';
import { COLORS, FONTS } from '../theme';

const { width, height } = Dimensions.get('window');

const ActivationScreen = () => {
  const [mode, setMode] = useState('select'); // 'select', 'scan', 'input'
  const [code, setCode] = useState('');
  const [permission, requestPermission] = useCameraPermissions();
  const { setPatientId, isLoading } = usePatientStore();

  const handleActivate = async (id) => {
    const success = await setPatientId(id);
    if (!success) {
      alert("Code invalide ou erreur serveur. Demandez à votre médecin.");
    }
  };

  const handleBarCodeScanned = ({ data }) => {
    setMode('select');
    handleActivate(data);
  };

  const onScanPress = async () => {
    if (!permission?.granted) {
      const { granted } = await requestPermission();
      if (!granted) {
        alert("Permission caméra requise pour scanner le QR Code.");
        return;
      }
    }
    setMode('scan');
  };

  if (mode === 'scan') {
    return (
      <View style={styles.cameraContainer}>
        <CameraView
          style={StyleSheet.absoluteFillObject}
          onBarcodeScanned={handleBarCodeScanned}
          barcodeScannerSettings={{
            barcodeTypes: ["qr"],
          }}
        />
        <View style={styles.overlay}>
          <View style={styles.unfocusedContainer}></View>
          <View style={styles.focusedRow}>
            <View style={styles.unfocusedContainer}></View>
            <View style={styles.focusedContainer}>
              <View style={styles.cornerTopLeft} />
              <View style={styles.cornerTopRight} />
              <View style={styles.cornerBottomLeft} />
              <View style={styles.cornerBottomRight} />
            </View>
            <View style={styles.unfocusedContainer}></View>
          </View>
          <View style={styles.unfocusedContainer}>
            <Text style={styles.scanText}>Scannez le QR Code de votre médecin</Text>
            <TouchableOpacity 
              style={styles.cancelButton} 
              onPress={() => setMode('select')}
            >
              <Text style={styles.cancelButtonText}>Annuler</Text>
            </TouchableOpacity>
          </View>
        </View>
      </View>
    );
  }

  return (
    <LinearGradient 
      colors={[COLORS.background, '#E0F2F1']} 
      style={styles.container}
    >
      <StatusBar barStyle="dark-content" />
      
      <View style={styles.header}>
        <Text style={styles.logo}>Hela</Text>
        <Text style={styles.tagline}>Votre compagnon de santé intelligent</Text>
      </View>

      {mode === 'select' ? (
        <View style={styles.choiceContainer}>
          <Text style={styles.instruction}>Comment souhaitez-vous activer votre app ?</Text>
          
          <TouchableOpacity onPress={onScanPress} style={styles.choiceCardWrapper}>
            <GlassCard style={styles.choiceCard}>
              <View style={styles.iconCircle}>
                <Ionicons name="qr-code-outline" size={32} color={COLORS.primary} />
              </View>
              <View style={styles.choiceTextContainer}>
                <Text style={styles.choiceTitle}>Scanner un QR Code</Text>
                <Text style={styles.choiceSubtitle}>Activation rapide chez le médecin</Text>
              </View>
              <Ionicons name="chevron-forward" size={24} color={COLORS.textSecondary} />
            </GlassCard>
          </TouchableOpacity>

          <TouchableOpacity onPress={() => setMode('input')} style={styles.choiceCardWrapper}>
            <GlassCard style={styles.choiceCard}>
              <View style={styles.iconCircle}>
                <Ionicons name="keypad-outline" size={32} color={COLORS.primary} />
              </View>
              <View style={styles.choiceTextContainer}>
                <Text style={styles.choiceTitle}>Saisir un Code</Text>
                <Text style={styles.choiceSubtitle}>Utilisez le code à 6 chiffres</Text>
              </View>
              <Ionicons name="chevron-forward" size={24} color={COLORS.textSecondary} />
            </GlassCard>
          </TouchableOpacity>
        </View>
      ) : (
        <View style={styles.inputContainer}>
          <TouchableOpacity 
            style={styles.backButton} 
            onPress={() => setMode('select')}
          >
            <Ionicons name="arrow-back" size={24} color={COLORS.text} />
            <Text style={styles.backText}>Retour</Text>
          </TouchableOpacity>

          <GlassCard style={styles.card}>
            <Text style={styles.label}>Saisissez votre code d'activation</Text>
            <TextInput
              style={styles.input}
              placeholder="000 000"
              value={code}
              onChangeText={setCode}
              keyboardType="number-pad"
              maxLength={6}
              placeholderTextColor="rgba(0,0,0,0.2)"
            />
            
            <TouchableOpacity 
              style={[styles.button, code.length < 6 && styles.buttonDisabled]} 
              onPress={() => handleActivate(code)}
              disabled={isLoading || code.length < 6}
            >
              {isLoading ? (
                <ActivityIndicator color={COLORS.white} />
              ) : (
                <Text style={styles.buttonText}>Activer mon application</Text>
              )}
            </TouchableOpacity>
          </GlassCard>
          
          <Text style={styles.hint}>
            Ce code vous a été remis par votre médecin lors de votre inscription.
          </Text>
        </View>
      )}

      <Text style={styles.footer}>Hela AI © 2026 - Biovatech Labs</Text>
    </LinearGradient>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, padding: 25, justifyContent: 'space-between' },
  header: { alignItems: 'center', marginTop: height * 0.1 },
  logo: { fontFamily: FONTS.bold, fontSize: 56, color: COLORS.primary, letterSpacing: -2 },
  tagline: { fontFamily: FONTS.regular, fontSize: 16, color: COLORS.textSecondary, marginTop: -5 },
  
  choiceContainer: { flex: 1, justifyContent: 'center' },
  instruction: { 
    fontFamily: FONTS.semibold, 
    fontSize: 18, 
    color: COLORS.text, 
    marginBottom: 25, 
    textAlign: 'center' 
  },
  choiceCardWrapper: { marginBottom: 15 },
  choiceCard: { 
    flexDirection: 'row', 
    alignItems: 'center', 
    padding: 20,
  },
  iconCircle: { 
    width: 60, 
    height: 60, 
    borderRadius: 30, 
    backgroundColor: 'rgba(0, 180, 219, 0.1)', 
    justifyContent: 'center', 
    alignItems: 'center' 
  },
  choiceTextContainer: { flex: 1, marginLeft: 15 },
  choiceTitle: { fontFamily: FONTS.bold, fontSize: 18, color: COLORS.text },
  choiceSubtitle: { fontFamily: FONTS.regular, fontSize: 14, color: COLORS.textSecondary },
  
  inputContainer: { flex: 1, justifyContent: 'center' },
  backButton: { flexDirection: 'row', alignItems: 'center', marginBottom: 20 },
  backText: { fontFamily: FONTS.medium, fontSize: 16, marginLeft: 5, color: COLORS.text },
  card: { padding: 30 },
  label: { 
    fontFamily: FONTS.medium, 
    fontSize: 16, 
    color: COLORS.text, 
    marginBottom: 25, 
    textAlign: 'center' 
  },
  input: { 
    backgroundColor: 'rgba(255,255,255,0.8)', 
    borderRadius: 20, 
    padding: 20, 
    fontSize: 36, 
    textAlign: 'center', 
    fontFamily: FONTS.bold,
    marginBottom: 25,
    borderWidth: 1,
    borderColor: COLORS.primary,
    color: COLORS.primaryDark,
    letterSpacing: 5
  },
  button: { 
    backgroundColor: COLORS.primary, 
    padding: 20, 
    borderRadius: 20, 
    alignItems: 'center',
    shadowColor: COLORS.primary,
    shadowOffset: { width: 0, height: 10 },
    shadowOpacity: 0.3,
    shadowRadius: 15,
    elevation: 8
  },
  buttonDisabled: { backgroundColor: '#B0BEC5', shadowOpacity: 0 },
  buttonText: { color: COLORS.white, fontFamily: FONTS.bold, fontSize: 18 },
  hint: { 
    marginTop: 20, 
    textAlign: 'center', 
    color: COLORS.textSecondary, 
    fontFamily: FONTS.regular,
    fontSize: 13,
    paddingHorizontal: 20
  },
  
  footer: { textAlign: 'center', color: 'rgba(0,0,0,0.3)', fontFamily: FONTS.regular, fontSize: 12, marginBottom: 10 },
  
  // Camera styles
  cameraContainer: { flex: 1, backgroundColor: 'black' },
  overlay: { flex: 1 },
  unfocusedContainer: { flex: 1, backgroundColor: 'rgba(0,0,0,0.7)', justifyContent: 'center', alignItems: 'center' },
  focusedRow: { flexDirection: 'row', height: 280 },
  focusedContainer: { width: 280, position: 'relative' },
  cornerTopLeft: { position: 'absolute', top: 0, left: 0, width: 40, height: 40, borderTopWidth: 5, borderLeftWidth: 5, borderColor: COLORS.primary },
  cornerTopRight: { position: 'absolute', top: 0, right: 0, width: 40, height: 40, borderTopWidth: 5, borderRightWidth: 5, borderColor: COLORS.primary },
  cornerBottomLeft: { position: 'absolute', bottom: 0, left: 0, width: 40, height: 40, borderBottomWidth: 5, borderLeftWidth: 5, borderColor: COLORS.primary },
  cornerBottomRight: { position: 'absolute', bottom: 0, right: 0, width: 40, height: 40, borderBottomWidth: 5, borderRightWidth: 5, borderColor: COLORS.primary },
  scanText: { color: 'white', fontFamily: FONTS.bold, fontSize: 18, marginBottom: 20 },
  cancelButton: { padding: 15, borderRadius: 30, backgroundColor: 'rgba(255,255,255,0.2)' },
  cancelButtonText: { color: 'white', fontFamily: FONTS.bold }
});

export default ActivationScreen;
