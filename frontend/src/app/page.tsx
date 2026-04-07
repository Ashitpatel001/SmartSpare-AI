import { redirect } from "next/navigation";

export default function RootPage() {
  // Automatically bounce all root traffic to the login screen
  redirect("/login");
}