# Progress Bar Implementation Guide

## 📦 Files Created

1. **`src/components/ui/ProgressBar.tsx`** - Progress bar component with animations
2. **`src/hooks/useProgressBar.ts`** - Hook and global functions to control progress bar
3. **Modified `src/components/api/api.service.tsx`** - Auto show/hide on API calls
4. **Modified `src/App.tsx`** - Added ProgressBar to root component

## 🎨 Features

- ✅ **Auto-tracking**: Automatically shows on API calls, hides on completion
- ✅ **Smooth animations**: Using Framer Motion for fluid transitions
- ✅ **Gradient effect**: Beautiful blue → purple → pink gradient
- ✅ **Smart progress**: Auto-simulates progress when not manually controlled
- ✅ **Global control**: Can be controlled from anywhere in the app
- ✅ **Non-blocking**: Doesn't interfere with refresh token flow

## 🚀 How It Works

### Automatic Mode (Default)

```tsx
// Progress bar automatically shows when any API call is made
// No code changes needed in your components!
```

### Manual Control (Optional)

```tsx
import {
  showProgressBar,
  hideProgressBar,
  updateProgress,
} from "@/hooks/useProgressBar";

// Start loading
showProgressBar();

// Update progress (0-100)
updateProgress(50);

// Complete and hide
hideProgressBar();
```

### Component Usage (Advanced)

```tsx
import { useProgressBar } from "@/hooks/useProgressBar";

function MyComponent() {
  const { startLoading, stopLoading, setProgress } = useProgressBar();

  const handleUpload = async () => {
    startLoading();
    try {
      // Your upload logic
      setProgress(50); // Optional manual progress
      await uploadFile();
    } finally {
      stopLoading();
    }
  };
}
```

## 🎯 Customization

### Change Colors

Edit `ProgressBar.tsx`:

```tsx
className = "h-full bg-gradient-to-r from-green-500 via-blue-500 to-teal-500";
```

### Change Height

```tsx
className = "fixed top-0 left-0 right-0 z-[9999] h-2 bg-transparent"; // Change h-1 to h-2
```

### Change Speed

```tsx
// In useEffect interval
}, 200); // Change from 300ms to 200ms for faster simulation
```

## 🧪 Testing

1. **Open browser DevTools** → Network tab → Throttle to "Slow 3G"
2. **Navigate** to any page with API calls (e.g., Dashboard)
3. **Observe** the top progress bar sliding smoothly
4. **Upload images** and watch progress bar appear automatically

## 🎭 Behavior

- **Shows**: When any API request starts (except refresh token)
- **Progress**: Auto-simulates 0% → 90% smoothly
- **Completes**: Jumps to 100% when request finishes
- **Hides**: Fades out after 500ms
- **Multiple requests**: Stays visible until all requests complete

## 🐛 Troubleshooting

### Progress bar not showing?

1. Check browser console for errors
2. Verify `framer-motion` is installed: `npm list framer-motion`
3. Ensure `useProgressBar()` is called in `App.tsx`

### Progress bar stuck?

- Check Network tab for pending requests
- Look for errors in axios interceptors
- Force hide: `hideProgressBar()` from console

### Want to disable for specific API?

Add condition in `api.service.tsx`:

```tsx
if (!url.includes("/auth/refresh") && !url.includes("/no-progress")) {
  showProgressBar();
}
```

## 📝 Notes

- z-index is set to 9999 to appear above all content
- Does not block user interaction
- Automatically handles concurrent requests
- Works with refresh token flow without showing
