import { IonIcon } from "@ionic/react";
import { checkmarkOutline, createOutline } from "ionicons/icons";
import useChat, { useSettings, useTheme } from "../../store/store";
import { motion } from "framer-motion";
import { useState } from "react";
import Modal from "../modals/Modal";
import ConfirmDelete from "../ConfirmDelete/ConfirmDelete";
import classNames from "classnames";
import { handleExportChats, handleImportChats } from "../../utils/importexport";
import { ImageSize } from "../../services/chatService";

const varinats = {
  hidden: { opacity: 0 },
  visible: { opacity: 1 },
  exit: { opacity: 0 },
};

export default function SettingsTab({ visible }: { visible: boolean }) {
  const [
    sendChatHistory,
    setSendChatHistory,
    dalleImageSize,
    setDalleImageSize,
  ] = useSettings((state) => [
    state.settings.sendChatHistory,
    state.setSendChatHistory,
    state.settings.dalleImageSize,
    state.setDalleImageSize,
  ]);

  const [theme, setTheme] = useTheme((state) => [state.theme, state.setTheme]);

  const clearAllChats = useChat((state) => state.clearAllChats);
  const [confirmDeleteChats, setConfirmDeleteChats] = useState(false);
  const [importExportStatus, setImportExportStatus] = useState({
    importing: false,
    exporting: false,
  });

  function handleOnChange(e: React.ChangeEvent<HTMLInputElement>) {
    setSendChatHistory(e.target.checked);
  }

  function handleChatsFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    setImportExportStatus({ importing: true, exporting: false });
    handleImportChats(file)
      .then(() => alert("Chats imported successfully"))
      .catch((message) => alert(message))
      .finally(() =>
        setImportExportStatus({ importing: false, exporting: false })
      );
  }

  function exportChats() {
    setImportExportStatus({ importing: false, exporting: true });
    handleExportChats()
      .then(() => alert("Chats exported successfully"))
      .catch((err) => alert(err))
      .finally(() =>
        setImportExportStatus({ importing: false, exporting: false })
      );
  }

  return (
    <motion.div
      variants={varinats}
      initial="hidden"
      animate="visible"
      exit="exit"
      className={classNames("settings", { hidden: !visible })}
    >
      <div className="p-2">
        <div className="flex items-center mb-4 justify-between border border-gray-200 rounded dark:border-gray-700 p-2">
          <div className="flex items-center">
            <label
              htmlFor="theme-toggle"
              className="ml-2 font-bold dark:text-gray-300 text-gray-700"
            >
              {theme === "dark" ? "Mode Sombre" : "Mode Clair"}
            </label>
            <span className="ml-2 text-xs text-gray-500 dark:text-gray-400">
              {theme === "dark" ? "🌙" : "☀️"}
            </span>
          </div>
          <label className="relative inline-flex items-center cursor-pointer">
            <input
              type="checkbox"
              id="theme-toggle"
              checked={theme === "dark"}
              onChange={() => setTheme(theme === "dark" ? "light" : "dark")}
              className="sr-only peer"
            />
            <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
          </label>
        </div>
        <div className="flex items-center mb-4 justify-between border border-gray-200 rounded dark:border-gray-700 p-2">
          <span className="ml-2 font-bold dark:text-gray-300">
            Clear all chats
          </span>
          <button
            type="button"
            className="bg-red-700 text-white p-1 px-2 rounded"
            onClick={() => setConfirmDeleteChats(true)}
          >
            Clear
          </button>
        </div>

        <div className="flex items-center mb-4 justify-between border border-gray-200 rounded dark:border-gray-700 p-2">
          <label
            htmlFor="default-checkbox"
            className="ml-2 font-bold dark:text-gray-300"
          >
            Send chat history
          </label>
          <label className="relative inline-flex items-center cursor-pointer">
            <input
              type="checkbox"
              value=""
              checked={sendChatHistory}
              className="sr-only peer"
              onChange={handleOnChange}
            />
            <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
          </label>
        </div>
        <div className="flex items-center mb-4 justify-between border border-gray-200 rounded dark:border-gray-700 p-2">
          <span className="ml-2 font-bold dark:text-gray-300">
            Import & Export Chats
          </span>
          <div className="flex items-center">
            <input
              type="file"
              name="chats-file"
              id="chats-file"
              accept=".json"
              onChange={handleChatsFileChange}
              className="hidden pointer-events-none"
            />
            <button
              type="button"
              className="bg-teal-700 text-white p-1 px-2 rounded mr-2 disabled:opacity-50 disabled:cursor-not-allowed disabled:pointer-events-none"
              onClick={() => document.getElementById("chats-file")?.click()}
              disabled={importExportStatus.importing}
            >
              Import
            </button>
            <button
              type="button"
              className="bg-red-700 text-white p-1 px-2 rounded disabled:cursor-not-allowed disabled:pointer-events-none"
              disabled={importExportStatus.exporting}
              onClick={exportChats}
            >
              Export
            </button>
          </div>
        </div>
      </div>
      <Modal visible={confirmDeleteChats}>
        <ConfirmDelete
          onDelete={() => {
            clearAllChats();
            setConfirmDeleteChats(false);
          }}
          onCancel={() => setConfirmDeleteChats(false)}
        >
          <p className="text-gray-500 dark:text-gray-700">
            This will delete all your chats and messages. This action cannot be
            undone.
          </p>
        </ConfirmDelete>
      </Modal>
    </motion.div>
  );
}