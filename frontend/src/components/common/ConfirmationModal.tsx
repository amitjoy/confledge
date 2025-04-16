import React, {useEffect, useRef} from 'react';
import {useTheme} from '../../contexts/ThemeProvider';

interface ConfirmationModalProps {
    title: string;
    message: string;
    onConfirm: () => void;
    onCancel: () => void;
}

const ConfirmationModal: React.FC<ConfirmationModalProps> = ({title, message, onConfirm, onCancel}) => {
    const {theme} = useTheme();
    const modalRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (modalRef.current && !modalRef.current.contains(event.target as Node)) {
                onCancel();
            }
        };

        document.addEventListener('mousedown', handleClickOutside);

        return () => {
            document.removeEventListener('mousedown', handleClickOutside);
        };
    }, [onCancel]);

    return (
        <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 z-50">
            <div ref={modalRef}
                 className={`p-6 rounded-lg shadow-lg max-w-sm w-full mx-auto ${theme === 'dark' ? 'bg-mauve-300 text-white' : 'bg-white text-black'}`}>
                <h2 className="text-xl font-semibold mb-4">{title}</h2>
                <p className="mb-4">{message}</p>
                <div className="flex justify-end">
                    <button
                        onClick={onCancel}
                        className="bg-gray-300 text-gray-700 px-4 py-2 rounded mr-2"
                    >
                        Cancel
                    </button>
                    <button
                        onClick={onConfirm}
                        className="bg-red-500 text-white px-4 py-2 rounded"
                    >
                        Delete
                    </button>
                </div>
            </div>
        </div>
    );
};

export default ConfirmationModal;
