import React, { useState } from 'react';

export default function OnboardingQuestionnaire() {
  const [currentStep, setCurrentStep] = useState(0);
  const [answers, setAnswers] = useState({
    medicalHistory: '',
    familyHistory: '',
    allergies: ''
  });

  const questions = [
    {
      id: 'medicalHistory',
      question: 'Have you ever been diagnosed with or treated for any illnesses? (including surgeries or hospitalizations)',
      type: 'textarea'
    },
    {
      id: 'familyHistory',
      question: 'Does anyone in your family have similar conditions or major illnesses (e.g., hypertension, diabetes, heart disease, cancer)?',
      type: 'textarea'
    },
    {
      id: 'allergies',
      question: 'Do you have any allergies to medications or food?',
      type: 'textarea'
    }
  ];

  const handleInputChange = (value: string) => {
    const currentQuestionId = questions[currentStep].id;
    setAnswers(prev => ({
      ...prev,
      [currentQuestionId]: value
    }));
  };

  const handleNext = () => {
    if (currentStep < questions.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      // Handle form completion
      alert('Questionnaire completed! Answers: ' + JSON.stringify(answers, null, 2));
    }
  };

  const handleBack = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const currentQuestion = questions[currentStep];
  const currentAnswer = answers[currentQuestion.id as keyof typeof answers] || '';

  return (
    <div style={{ padding: '40px 20px', maxWidth: '600px', margin: '0 auto', fontFamily: 'Arial, sans-serif' }}>
      {/* Header */}
      <div style={{ textAlign: 'center', marginBottom: '40px' }}>
        <h1 style={{ fontSize: '24px', marginBottom: '8px' }}>Medical History Questionnaire</h1>
        <p style={{ color: '#666', margin: 0 }}>Step {currentStep + 1} of {questions.length}</p>
      </div>

      {/* Question */}
      <div style={{ marginBottom: '40px' }}>
        <h2 style={{ fontSize: '18px', marginBottom: '20px', lineHeight: '1.4' }}>
          {currentQuestion.question}
        </h2>
        
        <textarea
          value={currentAnswer}
          onChange={(e) => handleInputChange(e.target.value)}
          placeholder="Please provide details or write 'None' if not applicable"
          style={{
            width: '100%',
            minHeight: '120px',
            padding: '12px',
            border: '1px solid #ccc',
            borderRadius: '4px',
            fontSize: '14px',
            fontFamily: 'Arial, sans-serif',
            resize: 'vertical',
            boxSizing: 'border-box'
          }}
        />
      </div>

      {/* Navigation Buttons */}
      <div style={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center',
        marginBottom: '40px' 
      }}>
        <button
          onClick={handleBack}
          disabled={currentStep === 0}
          style={{
            padding: '10px 20px',
            border: '1px solid #ccc',
            backgroundColor: currentStep === 0 ? '#f5f5f5' : 'white',
            color: currentStep === 0 ? '#999' : '#333',
            borderRadius: '4px',
            cursor: currentStep === 0 ? 'not-allowed' : 'pointer',
            fontSize: '14px'
          }}
        >
          Back
        </button>

        <button
          onClick={handleNext}
          style={{
            padding: '10px 20px',
            border: 'none',
            backgroundColor: '#007bff',
            color: 'white',
            borderRadius: '4px',
            cursor: 'pointer',
            fontSize: '14px'
          }}
        >
          {currentStep === questions.length - 1 ? 'Complete' : 'Next'}
        </button>
      </div>

      {/* Progress Dots */}
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        gap: '8px' 
      }}>
        {questions.map((_, index) => (
          <div
            key={index}
            style={{
              width: '12px',
              height: '12px',
              borderRadius: '50%',
              backgroundColor: index === currentStep ? '#007bff' : 
                              index < currentStep ? '#28a745' : '#dee2e6',
              cursor: 'pointer'
            }}
            onClick={() => setCurrentStep(index)}
          />
        ))}
      </div>
    </div>
  );
}