import React, { useState, useRef, useEffect } from 'react';
import { 
  View, Text, StyleSheet, FlatList, TextInput, 
  TouchableOpacity, KeyboardAvoidingView, Platform 
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import usePatientStore from '../store/usePatientStore';
import GlassCard from '../components/GlassCard';
import { COLORS, FONTS } from '../theme';

const ChatScreen = () => {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState([]);
  const [isThinking, setIsThinking] = useState(false);
  const [currentStep, setCurrentStep] = useState('');
  
  const { sendMessage } = usePatientStore();
  const flatListRef = useRef();

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage = { id: Date.now(), text: input, sender: 'user' };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsThinking(true);

    try {
      const response = await sendMessage(input);
      
      // Simulation des thinking_steps pour l'UI
      if (response.thinking_steps) {
        for (const step of response.thinking_steps) {
          setCurrentStep(step);
          await new Promise(r => setTimeout(r, 800));
        }
      }

      const helaMessage = {
        id: Date.now() + 1,
        text: response.hela_response,
        sender: 'hela',
        risk: response.risk_score,
        glossary: response.glossary_context
      };
      
      setMessages(prev => [...prev, helaMessage]);
    } catch (error) {
      console.error(error);
    } finally {
      setIsThinking(false);
      setCurrentStep('');
    }
  };

  const renderMessage = ({ item }) => (
    <View style={[
      styles.messageContainer, 
      item.sender === 'user' ? styles.userMessage : styles.helaMessage
    ]}>
      <GlassCard style={item.sender === 'user' ? styles.userCard : styles.helaCard}>
        <Text style={[
          styles.messageText, 
          item.sender === 'hela' && styles.arabicText
        ]}>
          {item.text}
        </Text>
        {item.risk && (
          <View style={[styles.riskBadge, { backgroundColor: COLORS[item.risk.toLowerCase()] || COLORS.primary }]}>
            <Text style={styles.riskText}>{item.risk}</Text>
          </View>
        )}
      </GlassCard>
    </View>
  );

  return (
    <KeyboardAvoidingView 
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'} 
      style={styles.container}
    >
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Hela AI</Text>
      </View>

      <FlatList
        ref={flatListRef}
        data={messages}
        renderItem={renderMessage}
        keyExtractor={item => item.id.toString()}
        contentContainerStyle={styles.chatList}
        onContentSizeChange={() => flatListRef.current?.scrollToEnd()}
      />

      {isThinking && (
        <View style={styles.thinkingContainer}>
          <Text style={styles.thinkingText}>{currentStep || "Hela yakhmem..."}</Text>
        </View>
      )}

      <View style={styles.inputContainer}>
        <TextInput
          style={styles.input}
          placeholder="Hkili, wash rak t'hess?..."
          value={input}
          onChangeText={setInput}
          multiline
        />
        <TouchableOpacity style={styles.sendButton} onPress={handleSend}>
          <Ionicons name="send" size={24} color={COLORS.white} />
        </TouchableOpacity>
      </View>
    </KeyboardAvoidingView>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: COLORS.background },
  header: { padding: 20, paddingTop: 60, backgroundColor: COLORS.white },
  headerTitle: { fontFamily: FONTS.bold, fontSize: 24, color: COLORS.primary },
  chatList: { padding: 20 },
  messageContainer: { marginVertical: 10, maxWidth: '85%' },
  userMessage: { alignSelf: 'flex-end' },
  helaMessage: { alignSelf: 'flex-start' },
  userCard: { backgroundColor: COLORS.primary },
  helaCard: { backgroundColor: COLORS.white },
  messageText: { fontFamily: FONTS.regular, fontSize: 16, color: COLORS.text },
  arabicText: { fontFamily: FONTS.arabic, textAlign: 'right', fontSize: 18 },
  riskBadge: { marginTop: 10, paddingHorizontal: 10, paddingVertical: 4, borderRadius: 12, alignSelf: 'flex-start' },
  riskText: { color: COLORS.white, fontSize: 12, fontFamily: FONTS.bold },
  thinkingContainer: { padding: 15, alignSelf: 'center' },
  thinkingText: { fontFamily: FONTS.medium, color: COLORS.primaryDark, fontStyle: 'italic' },
  inputContainer: { flexDirection: 'row', padding: 20, backgroundColor: COLORS.white, alignItems: 'center' },
  input: { flex: 1, backgroundColor: COLORS.background, borderRadius: 25, paddingHorizontal: 20, paddingVertical: 10, marginRight: 10, fontFamily: FONTS.regular },
  sendButton: { backgroundColor: COLORS.primary, width: 50, height: 50, borderRadius: 25, justifyContent: 'center', alignItems: 'center' },
});

export default ChatScreen;
