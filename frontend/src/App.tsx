import AnimatedNavbar from "./components/AnimatedNavbar";
import "./index.css";

export function App() {
  return (
    <div className="min-h-screen flex flex-col">
      <header className="w-full">
        <AnimatedNavbar />
      </header>
      <main className="flex-1 max-w-4xl mx-auto w-full px-4 py-8">
        {/* Content goes here */}
      </main>
    </div>
  );
}

export default App;
