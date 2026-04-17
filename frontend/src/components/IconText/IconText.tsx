import React, { useState } from 'react';
import { Space } from 'antd';

interface IconTextProps {
    iconOn: React.FC<{ style?: React.CSSProperties }>; // Icon to show when `value` is true
    iconOff: React.FC<{ style?: React.CSSProperties }>; // Icon to show when `value` is false
    text: string;
    onClick?: () => void; // Callback to handle click, passing the new value
    defaultValue?: boolean; // Initial state value
}


const IconText: React.FC<IconTextProps> = ({ iconOn, iconOff, text, onClick, defaultValue = false }) => {
    const [value, setValue] = useState(defaultValue);

    const handleClick = () => {
        const newValue = !value;
        setValue(newValue);
        if (onClick) {
            onClick(); // Notify parent with the new value
        }
    };

    return (
        <Space onClick={handleClick} style={{ cursor: onClick ? 'pointer' : 'default' }}>
            {React.createElement(value ? iconOn : iconOff)} {/* Toggle between icons based on `value` */}

            {text}
        </Space>
    );
};



export default IconText;
