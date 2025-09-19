'use client';

import type React from 'react';
import { X } from 'lucide-react';

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  subTitle?: string | null;
  children: React.ReactNode;
}

export function Modal({
  isOpen,
  onClose,
  title,
  subTitle,
  children,
}: ModalProps) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 p-4">
      <div className="w-full max-w-lg rounded-lg border border-zinc-800 bg-zinc-900">
        <div className="p-6">
          {/* Header */}
          <div className="mb-6 flex items-center justify-between">
            <h2 className="text-2xl font-bold text-white">{title}</h2>
            <button
              onClick={onClose}
              className="text-zinc-400 transition-colors hover:text-white"
            >
              <X size={24} />
            </button>
          </div>

          {subTitle && <p className="mb-6 text-zinc-400">{subTitle}</p>}

          {/* Body */}
          {children}
        </div>
      </div>
    </div>
  );
}

//
// 'use client';
//
// import type React from 'react';
// import { X } from 'lucide-react';
// import { Button } from '@/components/ui/button';
//
// interface ModalProps {
//   isOpen: boolean;
//   onClose: () => void;
//   title: string;
//   subTitle: string | null;
//   children: React.ReactNode;
//   onSubmit?: () => void;
//   submitText?: string;
//   submitDisabled?: boolean;
//   isSubmitting?: boolean;
// }
//
// export function Modal({
//   isOpen,
//   onClose,
//   title,
//   subTitle,
//   children,
//   onSubmit,
//   submitText = 'Submit',
//   submitDisabled = false,
//   isSubmitting = false,
// }: ModalProps) {
//   if (!isOpen) return null;
//
//   return (
//     <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 p-4">
//       <div className="w-full max-w-lg rounded-lg border border-zinc-800 bg-zinc-900">
//         <div className="p-6">
//           <div className="mb-6 flex items-center justify-between">
//             <h2 className="text-2xl font-bold text-white">{title}</h2>
//             <button
//               onClick={onClose}
//               className="text-zinc-400 transition-colors hover:text-white"
//             >
//               <X size={24} />
//             </button>
//           </div>
//           <p className="mb-6 text-zinc-400">{subTitle}</p>
//
//           {children}
//
//           <div className="flex gap-3 pt-6">
//             {onSubmit && (
//               <Button
//                 onClick={onSubmit}
//                 disabled={submitDisabled || isSubmitting}
//                 className="flex-1 bg-white text-black hover:bg-zinc-200 disabled:opacity-50"
//               >
//                 {isSubmitting ? 'Please wait...' : submitText}
//               </Button>
//             )}
//             <Button
//               type="button"
//               variant="outline"
//               onClick={onClose}
//               className="flex-1 border-zinc-700 bg-transparent text-zinc-300 hover:bg-zinc-800 hover:text-white"
//             >
//               Cancel
//             </Button>
//           </div>
//         </div>
//       </div>
//     </div>
//   );
// }
