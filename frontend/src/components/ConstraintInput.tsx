import React, { useState } from 'react';

interface ConstraintInputProps {
  onConstraintChange: (constraint: string) => void;
  disabled?: boolean;
}

export const ConstraintInput: React.FC<ConstraintInputProps> = ({
  onConstraintChange,
  disabled = false
}) => {
  const [constraint, setConstraint] = useState('');
  
  const handleChange = (event: React.ChangeEvent<HTMLTextAreaElement>) => {
    const value = event.target.value;
    setConstraint(value);
    onConstraintChange(value);
  };

  const exampleConstraints = [
    "Connect with 5cm distance between centers",
    "Mount vertically with 3cm gap",
    "Attach at 45-degree angle, 2cm apart",
    "Align horizontally with 10mm separation"
  ];

  return (
    <div style={{ padding: '20px', border: '1px solid #ddd', borderRadius: '8px' }}>
      <h3 style={{ margin: '0 0 16px 0', fontSize: '18px' }}>Assembly Instructions</h3>
      
      <textarea
        value={constraint}
        onChange={handleChange}
        disabled={disabled}
        placeholder="Describe how the parts should be connected..."
        style={{
          width: '100%',
          minHeight: '100px',
          padding: '12px',
          border: '1px solid #ccc',
          borderRadius: '4px',
          fontSize: '14px',
          resize: 'vertical',
          backgroundColor: disabled ? '#f5f5f5' : 'white'
        }}
      />
      
      <div style={{ marginTop: '12px' }}>
        <div style={{ fontSize: '12px', color: '#666', marginBottom: '8px' }}>
          Examples:
        </div>
        {exampleConstraints.map((example, index) => (
          <button
            key={index}
            onClick={() => !disabled && handleChange({ target: { value: example } } as any)}
            disabled={disabled}
            style={{
              display: 'block',
              width: '100%',
              textAlign: 'left',
              padding: '8px 12px',
              margin: '4px 0',
              border: '1px solid #e0e0e0',
              borderRadius: '4px',
              backgroundColor: disabled ? '#f5f5f5' : '#f8f9fa',
              cursor: disabled ? 'not-allowed' : 'pointer',
              fontSize: '12px',
              color: disabled ? '#999' : '#333'
            }}
          >
            {example}
          </button>
        ))}
      </div>
      
      {constraint && (
        <div style={{ 
          marginTop: '12px', 
          padding: '8px', 
          backgroundColor: '#e3f2fd', 
          borderRadius: '4px',
          fontSize: '12px'
        }}>
          <strong>Current instruction:</strong> {constraint}
        </div>
      )}
    </div>
  );
};