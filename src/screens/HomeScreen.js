import React, { useState } from 'react';
import { 
  View, Text, StyleSheet, ScrollView, 
  TouchableOpacity, Modal, Dimensions 
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { Ionicons } from '@expo/vector-icons';
import QRCode from 'react-native-qrcode-svg';
import usePatientStore from '../store/usePatientStore';
import GlassCard from '../components/GlassCard';
import { COLORS, FONTS } from '../theme';

const { width } = Dimensions.get('window');

const HomeScreen = () => {
  const { profile, patientId, verificationOtp } = usePatientStore();
  const [showQrModal, setShowQrModal] = useState(false);

  return (
    <View style={styles.container}>
      <ScrollView style={styles.scrollView}>
        <LinearGradient colors={[COLORS.primary, COLORS.primaryDark]} style={styles.header}>
          <View style={styles.headerTop}>
            <View>
              <Text style={styles.greeting}>Saha, {profile?.name || 'Ammi/Khalti'}! 👋</Text>
              <Text style={styles.subtitle}>Comment te sens-tu aujourd'hui ?</Text>
            </View>
            <TouchableOpacity 
              style={styles.qrButton} 
              onPress={() => setShowQrModal(true)}
            >
              <Ionicons name="qr-code" size={24} color={COLORS.white} />
            </TouchableOpacity>
          </View>
        </LinearGradient>

        <View style={styles.content}>
          <GlassCard style={styles.nurtureCard}>
            <View style={styles.nurtureHeader}>
              <Ionicons name="sparkles" size={20} color={COLORS.primary} />
              <Text style={styles.nurtureTitle}>Conseil de Hela AI</Text>
            </View>
            <Text style={styles.nurtureText}>
              "Labess? Matnesaych dwa dialek lyoum, sahtek hiya el sah. Chrab chwiya l'ma kman."
            </Text>
          </GlassCard>

          <View style={styles.statsRow}>
            <GlassCard style={styles.statCard}>
              <Ionicons name="heart" size={24} color={COLORS.danger} />
              <Text style={styles.statLabel}>Tension</Text>
              <Text style={styles.statValue}>13/8</Text>
              <Text style={styles.statTrend}>Stable</Text>
            </GlassCard>
            <GlassCard style={styles.statCard}>
              <Ionicons name="water" size={24} color={COLORS.primary} />
              <Text style={styles.statLabel}>Glycémie</Text>
              <Text style={styles.statValue}>1.10</Text>
              <Text style={styles.statTrend}>Normal</Text>
            </GlassCard>
          </View>

          <TouchableOpacity style={styles.actionButton}>
            <LinearGradient 
              colors={[COLORS.primary, COLORS.primaryDark]} 
              start={{x: 0, y: 0}} 
              end={{x: 1, y: 0}}
              style={styles.actionGradient}
            >
              <Ionicons name="add-circle" size={24} color={COLORS.white} />
              <Text style={styles.actionButtonText}>Prendre mes mesures</Text>
            </LinearGradient>
          </TouchableOpacity>
        </View>
      </ScrollView>

      {/* QR Modal for Clinic Linking */}
      <Modal
        visible={showQrModal}
        transparent={true}
        animationType="slide"
        onRequestClose={() => setShowQrModal(false)}
      >
        <View style={styles.modalOverlay}>
          <GlassCard style={styles.modalCard}>
            <TouchableOpacity 
              style={styles.closeModal} 
              onPress={() => setShowQrModal(false)}
            >
              <Ionicons name="close" size={28} color={COLORS.text} />
            </TouchableOpacity>

            <Text style={styles.modalTitle}>Lier à une clinique</Text>
            <Text style={styles.modalSubtitle}>
              Montrez ce code à votre médecin pour qu'il puisse accéder à votre dossier Hela.
            </Text>

            <View style={styles.qrContainer}>
              <QRCode
                value={patientId || 'NO_ID'}
                size={200}
                color={COLORS.text}
                backgroundColor={COLORS.white}
              />
            </View>

            <View style={styles.otpContainer}>
              <Text style={styles.otpLabel}>Code de vérification</Text>
              <Text style={styles.otpValue}>{verificationOtp}</Text>
            </View>

            <Text style={styles.modalNote}>
              Ce code expire dans 5 minutes pour votre sécurité.
            </Text>
          </GlassCard>
        </View>
      </Modal>
    </View>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: COLORS.background },
  scrollView: { flex: 1 },
  header: { padding: 30, paddingTop: 60, borderBottomLeftRadius: 40, borderBottomRightRadius: 40 },
  headerTop: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  greeting: { fontFamily: FONTS.bold, fontSize: 26, color: COLORS.white },
  subtitle: { fontFamily: FONTS.regular, fontSize: 16, color: 'rgba(255,255,255,0.8)', marginTop: 5 },
  qrButton: { 
    backgroundColor: 'rgba(255,255,255,0.2)', 
    padding: 12, 
    borderRadius: 15,
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.3)'
  },
  content: { padding: 20 },
  nurtureCard: { marginBottom: 25, padding: 20 },
  nurtureHeader: { flexDirection: 'row', alignItems: 'center', marginBottom: 10 },
  nurtureTitle: { fontFamily: FONTS.bold, fontSize: 16, color: COLORS.primary, marginLeft: 8 },
  nurtureText: { 
    fontFamily: FONTS.arabic, 
    fontSize: 20, 
    textAlign: 'right', 
    color: COLORS.text,
    lineHeight: 30
  },
  statsRow: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 25 },
  statCard: { width: '47%', alignItems: 'center', padding: 15 },
  statLabel: { fontFamily: FONTS.medium, fontSize: 13, color: COLORS.textSecondary, marginTop: 10 },
  statValue: { fontFamily: FONTS.bold, fontSize: 22, color: COLORS.text, marginTop: 5 },
  statTrend: { fontFamily: FONTS.regular, fontSize: 12, color: COLORS.success, marginTop: 2 },
  actionButton: { borderRadius: 20, overflow: 'hidden', elevation: 5 },
  actionGradient: { 
    flexDirection: 'row', 
    alignItems: 'center', 
    justifyContent: 'center', 
    padding: 20 
  },
  actionButtonText: { fontFamily: FONTS.bold, fontSize: 18, color: COLORS.white, marginLeft: 10 },
  
  // Modal styles
  modalOverlay: { 
    flex: 1, 
    backgroundColor: 'rgba(0,0,0,0.6)', 
    justifyContent: 'center', 
    padding: 20 
  },
  modalCard: { padding: 30, alignItems: 'center' },
  closeModal: { alignSelf: 'flex-end', marginBottom: 10 },
  modalTitle: { fontFamily: FONTS.bold, fontSize: 24, color: COLORS.text },
  modalSubtitle: { 
    fontFamily: FONTS.regular, 
    fontSize: 14, 
    color: COLORS.textSecondary, 
    textAlign: 'center',
    marginTop: 10,
    marginBottom: 25
  },
  qrContainer: { 
    padding: 20, 
    backgroundColor: COLORS.white, 
    borderRadius: 20,
    elevation: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 10 },
    shadowOpacity: 0.1,
    shadowRadius: 15,
  },
  otpContainer: { marginTop: 30, alignItems: 'center' },
  otpLabel: { fontFamily: FONTS.medium, fontSize: 14, color: COLORS.textSecondary },
  otpValue: { 
    fontFamily: FONTS.bold, 
    fontSize: 32, 
    color: COLORS.primaryDark, 
    letterSpacing: 5,
    marginTop: 5
  },
  modalNote: { 
    fontFamily: FONTS.regular, 
    fontSize: 12, 
    color: COLORS.textSecondary, 
    marginTop: 30,
    fontStyle: 'italic'
  }
});

export default HomeScreen;
