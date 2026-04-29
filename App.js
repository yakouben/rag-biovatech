import React, { useState, useEffect, useCallback } from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { Ionicons } from '@expo/vector-icons';
import * as Font from 'expo-font';
import * as SplashScreen from 'expo-splash-screen';
import { View } from 'react-native';

import usePatientStore from './src/store/usePatientStore';
import ActivationScreen from './src/screens/ActivationScreen';
import HomeScreen from './src/screens/HomeScreen';
import ChatScreen from './src/screens/ChatScreen';
import { COLORS } from './src/theme';

SplashScreen.preventAutoHideAsync();

const Tab = createBottomTabNavigator();

export default function App() {
  const [appIsReady, setAppIsReady] = useState(false);
  const { patientId } = usePatientStore();

  useEffect(() => {
    async function prepare() {
      try {
        await Font.loadAsync({
          'Urbanist-Bold': require('./assets/fonts/Urbanist-Bold.ttf'),
          'Urbanist-SemiBold': require('./assets/fonts/Urbanist-SemiBold.ttf'),
          'Urbanist-Medium': require('./assets/fonts/Urbanist-Medium.ttf'),
          'Urbanist-Regular': require('./assets/fonts/Urbanist-Regular.ttf'),
          'Amiri-Regular': require('./assets/fonts/Amiri-Regular.ttf'),
        });
      } catch (e) {
        console.warn(e);
      } finally {
        setAppIsReady(true);
      }
    }
    prepare();
  }, []);

  const onLayoutRootView = useCallback(async () => {
    if (appIsReady) {
      await SplashScreen.hideAsync();
    }
  }, [appIsReady]);

  if (!appIsReady) {
    return null;
  }

  return (
    <View style={{ flex: 1 }} onLayout={onLayoutRootView}>
      {!patientId ? (
        <ActivationScreen />
      ) : (
        <NavigationContainer>
          <Tab.Navigator
            screenOptions={({ route }) => ({
              tabBarIcon: ({ focused, color, size }) => {
                let iconName;
                if (route.name === 'Accueil') iconName = 'home';
                else if (route.name === 'Hela AI') iconName = 'chatbubble-ellipses';
                return <Ionicons name={iconName} size={size} color={color} />;
              },
              tabBarActiveTintColor: COLORS.primary,
              tabBarInactiveTintColor: 'gray',
              headerShown: false,
              tabBarStyle: {
                height: 70,
                paddingBottom: 10,
                backgroundColor: COLORS.white,
                borderTopWidth: 0,
                elevation: 10
              }
            })}
          >
            <Tab.Screen name="Accueil" component={HomeScreen} />
            <Tab.Screen name="Hela AI" component={ChatScreen} />
          </Tab.Navigator>
        </NavigationContainer>
      )}
    </View>
  );
}
